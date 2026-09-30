defmodule Receipts do
  def total(prices), do: PriceMath.sum(prices)
  def remember(prices), do: GenServer.call(Receipts.Store, {:remember, total(prices)})
  def history, do: GenServer.call(Receipts.Store, :history)
end
