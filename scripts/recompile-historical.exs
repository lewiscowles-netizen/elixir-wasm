defmodule ElixirWasm.Retargeter do
  def wrap_calls(term) when is_list(term), do: Enum.map(term, &wrap_calls/1)
  def wrap_calls(term) when is_tuple(term) do
    term = term |> Tuple.to_list() |> Enum.map(&wrap_calls/1) |> List.to_tuple()
    case term do
      {:call, line, {:remote, _, {:atom, _, module}, {:atom, _, function}} = target, [tree | arguments]}
      when (module == :compile and function in [:forms, :noenv_forms]) or (module == :erl_eval and function in [:expr, :exprs, :check_command]) ->
        normalized = {:call, line, {:remote, line, {:atom, line, :elixir_wasm_compat}, {:atom, line, :normalize}}, [tree]}
        {:call, line, target, [normalized | arguments]}
      other -> other
    end
  end
  def wrap_calls(term), do: term
end

root = "/src/selected-elixir/lib"
results =
  for path <- Path.wildcard(root <> "/*/ebin/*.beam") do
    {module, forms} =
      if File.exists?(path <> ".forms") do
        forms = path <> ".forms" |> File.read!() |> :erlang.binary_to_term()
        {:attribute, _, :module, module} = Enum.find(forms, &match?({:attribute, _, :module, _}, &1))
        File.rm!(path <> ".forms")
        {module, forms}
      else
        {:ok, {module, [{:abstract_code, {:raw_abstract_v1, forms}}]}} = :beam_lib.chunks(String.to_charlist(path), [:abstract_code])
        {module, forms}
      end
    forms = Enum.reject(forms, fn
      {:attribute, _, name, _} when name in [:type, :opaque, :spec, :export_type, :callback, :optional_callbacks] -> true
      _ -> false
    end)
    forms = Enum.map(forms, fn
      {:attribute, line, :record, {name, fields}} ->
        fields = Enum.map(fields, fn
          {:typed_record_field, field, _type} -> field
          field -> field
        end)
        {:attribute, line, :record, {name, fields}}
      form -> form
    end)
    forms = Enum.map(forms, fn form ->
      :erl_parse.map_anno(fn
        line when is_integer(line) and line < 0 -> :erl_anno.set_generated(true, :erl_anno.new(-line))
        annotation -> annotation
      end, form)
    end)
    forms = Enum.map(forms, fn
      {:function, _, _, _, _} = form -> ElixirWasm.Retargeter.wrap_calls(form)
      form -> form
    end)
    binary =
      case :compile.forms(forms, [:binary, :debug_info, :return_errors, :return_warnings]) do
        {:ok, ^module, binary} -> binary
        {:ok, ^module, binary, _warnings} -> binary
        failure -> raise "Cannot retarget #{path}: #{inspect(failure)}"
      end
    File.write!(path, binary)
    module
  end
IO.puts("Recompiled #{length(results)} historical modules with OTP #{System.otp_release()}")
{:ok, :elixir_wasm_compat} = :compile.file(~c"/builder/elixir_wasm_compat.erl", [{:outdir, String.to_charlist(root <> "/elixir/ebin")}, :debug_info, :report])
[{:application, :elixir, properties}] = :file.consult(~c"/src/selected-elixir/lib/elixir/ebin/elixir.app") |> elem(1)
properties = Keyword.update!(properties, :applications, &List.delete(&1, :crypto))
File.write!("/src/selected-elixir/lib/elixir/ebin/elixir.app", :io_lib.format(~c"~p.~n", [{:application, :elixir, properties}]))

File.mkdir_p!("/bundle")
File.write!("/bundle/retargeting.json", :json.encode(%{
  "method" => "Recompile preserved Erlang abstract forms with OTP 29",
  "originalCompilerOtp" => System.get_env("HISTORICAL_OTP") || "17.5",
  "originalCompilerImage" => System.get_env("HISTORICAL_IMAGE"),
  "sourcePatch" => "families/historical/stdio.patch (only where the obsolete option exists)",
  "changes" => ["Use encoding=utf8 for legacy stderr initialization where required", "Recompile BEAM abstract forms without legacy type/spec/callback attributes or record field types, preserving record fields and defaults", "Normalize negative legacy generated-code line annotations at build time and before runtime evaluation/compilation", "Remove unconditional crypto application startup dependency"],
  "compatibility" => "Experimental; not an authentic historical OTP runtime"
}))
