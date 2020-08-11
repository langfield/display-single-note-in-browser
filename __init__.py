from aqt import gui_hooks, mw
from aqt.browser import SearchContext
from PyQt5 import QtWidgets
from anki.utils import ids2str
from aqt.browser import Browser

from .config import getUserOption, setUserOption


def one_by_note(ctx: SearchContext):
    if not getUserOption("One card by note", True):
        return
    nids = set()
    filtered_card = []
    selected_card = mw.reviewer.card
    selected_cid = selected_card.id if selected_card else 0
    selected_nid = selected_card.nid if selected_card else 0
    idx_of_selected_note = None
    # position of the unique card of note currently in reviewer

    for cid in ctx.card_ids:
        nid = mw.col.db.scalar("select nid from cards where id = ?", cid)
        if nid not in nids:
            filtered_card.append(cid)
            nids.add(nid)
            if nid == selected_nid:
                idx_of_selected_note = len(filtered_card) - 1
        elif cid == selected_cid:  # nid in nids
            filtered_card.pop(idx_of_selected_note)
            filtered_card.append(cid)
    ctx.card_ids = filtered_card


gui_hooks.browser_did_search.append(one_by_note)


def will_show(browser):
    browser.form.action_only_note = QtWidgets.QAction(browser)
    browser.form.menu_Notes.addAction(browser.form.action_only_note)
    browser.form.action_only_note.setText("Card/Note")
    browser.form.action_only_note.setShortcut(
            getUserOption("Shortcut", "Ctrl+Alt+N"))
    browser.form.action_only_note.triggered.connect(lambda: on_card_note(browser))


def on_card_note(browser):
    setUserOption("One card by note", not getUserOption(
        "One card by note", True))
    browser.onSearchActivated()
    


gui_hooks.browser_will_show.append(will_show)

def selectedCards(browser):
    cids = [
        browser.model.cards[idx.row()]
        for idx in browser.form.tableView.selectionModel().selectedRows()
    ]
    if getUserOption("One card by note", True) and getUserOption("Action to note", True):
        query = f"select card.id from cards as card where card.nid in (select nid from cards as model_card where model_card.id in {ids2str(cids)})"
        cids = browser.col.db.list(query)
    return cids


Browser.selectedCards = selectedCards
