from deconnected.runtime.gui import run_gui_journey

result = run_gui_journey(
    "http://localhost:3000",
    [{"goto": "/orders"}, {"click": "text=Open first order"}],
)
print(result.api_urls)
