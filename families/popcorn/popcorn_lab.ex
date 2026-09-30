defmodule PopcornLab do
  use Application
  def start(_type, _args) do
    Supervisor.start_link([Popcorn.Proxy, PopcornLab.Evaluator], strategy: :one_for_one)
  end
end

defmodule PopcornLab.Evaluator do
  use GenServer
  def start_link(_args), do: GenServer.start_link(__MODULE__, 0, name: :lab_evaluator)
  def init(count), do: {:ok, count}
  def handle_call(["add", amount], _from, count) do
    {:reply, count + amount, count + amount}
  end
  def handle_call(["eval", source], _from, count) do
    result = try do
      {value, _bindings} = Code.eval_string(source, [], file: "/main.exs")
      %{"ok" => true, "value" => inspect(value)}
    rescue
      error -> %{"ok" => false, "error" => Exception.format(:error, error, __STACKTRACE__)}
    catch
      kind, reason -> %{"ok" => false, "error" => Exception.format(kind, reason, __STACKTRACE__)}
    end
    {:reply, result, count}
  end
end
