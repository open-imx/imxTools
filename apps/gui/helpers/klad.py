from nicegui import ui


class ExampleCard:
    def __init__(self, index):
        self.index = index

    def build(self):
        # Just RETURN a card, don’t mount it inside self!
        card = ui.card().classes("p-4 shadow w-72 flex-none relative")
        with card:
            ui.label(f"Result #{self.index}").classes("text-lg font-bold")
            ui.label("Details here.")
            ui.button("Close", on_click=lambda: card.delete())
        return card


class ResultArea:
    def __init__(self):
        self.container = ui.row().classes(
            "w-full flex-wrap content-start gap-4 p-4 overflow-auto"
        )
        self.cards = []

    def add_card(self):
        card = ExampleCard(len(self.cards) + 1)
        self.cards.append(card)
        # ✅ BUILD CARD, THEN ATTACH IT HERE:
        with self.container:
            card.build()


result_area = ResultArea()

ui.button("Add Card", on_click=result_area.add_card).classes("m-4")

ui.run()
