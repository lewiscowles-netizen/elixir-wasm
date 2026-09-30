defmodule Receipts.Application do
  use Application

  def start(_type, _args) do
    Supervisor.start_link([Receipts.Store], strategy: :one_for_one, name: Receipts.Supervisor)
  end
end
