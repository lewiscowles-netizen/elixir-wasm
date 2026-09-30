defmodule PriceMath do
  def sum(prices), do: Enum.reduce(prices, 0, fn price, total -> price + total end)
end
