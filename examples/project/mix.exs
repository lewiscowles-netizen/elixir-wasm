defmodule Receipts.MixProject do
  use Mix.Project

  def project do
    [app: :receipts, version: "0.1.0", elixir: "~> 1.18", deps: [{:price_math, path: "vendor/price_math"}]]
  end

  def application do
    [mod: {Receipts.Application, []}]
  end
end
