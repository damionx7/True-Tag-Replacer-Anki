from aqt.qt import *
from aqt.utils import getText, tooltip, showInfo
from aqt.tagedit import TagEdit
from anki.hooks import addHook
from anki.lang import _

# https://github.com/glutanimate/anki-addons-misc/blob/master/src/browser_replace_tag/browser_replace_tag.py

def myGetTag(parent, deck, question, tags="user", taglist=None, **kwargs):
    te = TagEdit(parent)
    te.setCol(deck)
    if taglist is not None:
        # set tag list manually
        te.model.setStringList(taglist)
    ret = getText(question, parent, edit=te, **kwargs)
    te.hideCompleter()
    return ret

def replaceTag(self):
    mw = self.mw
    selected = self.selectedNotes()
    if not selected:
        tooltip("No cards selected.", period=2000)
        return
    
    firstNote =  mw.col.getNote(selected[0])
    msg = "Which tag would you like to replace?<br>Please select just one."
    (oldTag, r) = myGetTag(self, mw.col, msg, taglist=firstNote.tags, title="Choose tag")
    if not r or not oldTag.strip():
        return
    oldTag = oldTag.split()[0]

    msg = "Which tag would you like to replace %s with?" % oldTag
    (newTag, r) = myGetTag(self, mw.col, msg, title="Replace Tag", default=oldTag)
    if not r or not newTag.strip():
        return

    print("newTag %s , oldTag %s" % (newTag , oldTag))

    mw.checkpoint("replace tag")
    mw.progress.start()
    self.model.beginReset()
    for nid in selected:
        note = mw.col.getNote(nid)
        tags = note.tags

        for _tag in tags.copy():
          print("operating on " + _tag + "\n")
          # old tags contains :: means its meta tag
          if(len(oldTag.split("::")) > 1):
            print("> criteria contains ::" + "\n")
            if(oldTag in _tag):
                print("> found " + oldTag + " in " + _tag + " in Meta (::) Routine" + "\n")
                tagToFeed = _tag.replace(oldTag, newTag)
                note.delTag(_tag)
                note.addTag(tagToFeed)
                note.flush()
                print("> replaced " + _tag + " with " + tagToFeed + "\n")
          else:
            _tag_split = _tag.split("::")
            if(len(_tag_split) > 1):
              print("> tag with ::" + "\n")
              if(oldTag in _tag_split):
                print("> found " + oldTag + " in " + _tag + "\n")
                tagToFeed = _tag.replace(oldTag, newTag)
                note.delTag(_tag)
                note.addTag(tagToFeed)
                note.flush()
                print("> replaced " + _tag + " with " + tagToFeed + "\n")
            else:
              print("> single tag without ::" + "\n")
              if(oldTag == _tag):
                print(">" + oldTag + " equals " + _tag + "\n")
                tagToFeed = _tag.replace(oldTag, newTag)
                note.delTag(_tag)
                note.addTag(tagToFeed)
                note.flush()
                print("> replaced " + _tag + " with " + tagToFeed + "\n")
    self.model.endReset()
    mw.requireReset()
    mw.progress.finish()
    mw.reset()
    tooltip("Tag replaced. <br>Use 'Check Database' to remove unused tags.")

def setupMenu(self):
    try:
        menu = self.menuBrowserCustom
    except:
        self.menuBrowserCustom = QMenu(_("Custom"))
        action = self.menuBar().insertMenu(self.mw.form.menuTools.menuAction(), self.menuBrowserCustom)
    menu = self.menuBrowserCustom
    menu.addSeparator()
    a = menu.addAction('Replace Tag...')
    a.triggered.connect(lambda _, b=self: replaceTag(b))

addHook("browser.setupMenus", setupMenu)