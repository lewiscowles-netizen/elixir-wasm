# Why compile before loading AtomVM?

AtomVM implements the BEAM instruction set with a smaller runtime and a selected set of Erlang and Elixir libraries. The native Elixir compiler can therefore produce a program for it without shipping the full compiler into the browser.

This changes the development loop. With the OTP routes, an editor sends source to a compiler already running inside the browser. With stock AtomVM, the builder compiles the script, packages its bytecode and libraries, and sends those files to the browser. Changing a textarea would not change the compiled program, so the AtomVM editor is intentionally read-only.

The compiler version and runtime library version are separate facts. Compiling with Elixir 1.17.3 does not make every Elixir 1.17.3 function available on AtomVM. A call can compile successfully and still fail when the smaller runtime cannot resolve its module, function or built-in operation. Native and browser probes check different parts of that boundary.

This route contains no Popcorn code. It uses upstream AtomVM's Emscripten port with visible module/export options for the lab adapter. Its library subset stays coherent with its VM; the recipe does not fill gaps by copying arbitrary OTP libraries into it.

The smaller deployment is useful for focused computations and message-driven programs that fit the supported surface. The [AtomVM tutorial](../tutorials/05-atomvm.md) demonstrates arithmetic, library calls and process messages. Full server releases, runtime compilation and unrestricted Mix dependency graphs require a different compatibility investigation.
