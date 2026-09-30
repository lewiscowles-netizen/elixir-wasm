defmodule Receipts.Store do
  use GenServer

  def start_link(_args), do: GenServer.start_link(__MODULE__, [], name: __MODULE__)
  def init(history), do: {:ok, history}
  def handle_call({:remember, total}, _from, history), do: {:reply, total, [total | history]}
  def handle_call(:history, _from, history), do: {:reply, Enum.reverse(history), history}
end
