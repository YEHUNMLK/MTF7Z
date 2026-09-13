import os
import sys
import hashlib
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt, QTranslator, QSettings, QCoreApplication
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QMainWindow, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QToolBar, QStatusBar,
    QComboBox, QWidget, QVBoxLayout, QFrame, QLabel,
    QToolButton, QMenu, QSizePolicy
)


def find_7z():
    for name in ("7z", "7zz"):
        path = shutil.which(name)
        if path:
            return path
    return None


SEVEN_Z = find_7z()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def file_signature(path: Path):
    if not path.exists():
        return None
    st = path.stat()
    return (st.st_size, st.st_mtime_ns, sha256_file(path))


@dataclass
class EditedFile:
    archive_path: str
    temp_path: Path
    original_signature: tuple | None
    updated_signature: tuple | None = None
    status: str = "Extracted"

    def current_signature(self):
        return file_signature(self.temp_path)

    def modified(self):
        return self.current_signature() != self.original_signature


class ArchiveError(RuntimeError):
    pass


class Archive:
    def __init__(self, path: Path):
        self.path = path
    
    # List files and directories in the 7z archive
    def list_files(self):
        p = subprocess.run(
            [SEVEN_Z, "l", "-slt", "-ba", str(self.path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
        )
        if p.returncode != 0:
            raise ArchiveError(p.stderr.strip() or self.tr("Unable to read the 7z archive"))

        records = []
        current = {}

        for line in p.stdout.splitlines():
            if not line.strip():
                if "Path" in current:
                    records.append(current)
                current = {}
                continue

            if " = " in line:
                key, value = line.split(" = ", 1)
                current[key.strip()] = value

        if "Path" in current:
            records.append(current)

        result = []
        for r in records:
            path = r.get("Path", "")
            attrs = r.get("Attributes", "")
            # 7-Zip header records may occur before actual archive entries.
            if not path or path == str(self.path):
                continue

            is_dir = "D" in attrs
            result.append((path.replace("\\", "/"), is_dir))

        return result

    # Extract a file from the 7z archive
    def extract_one(self, archive_name: str, destination: Path):
        destination.mkdir(parents=True, exist_ok=True)
        p = subprocess.run(
            [
                SEVEN_Z, "x", "-y",
                str(self.path),
                archive_name,
                f"-o{destination}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            errors="replace",
        )

        if p.returncode != 0:
            raise ArchiveError(p.stderr.strip() or self.tr("Failed to extract: {archive_name}").format(archive_name=archive_name))

        target = destination / archive_name
        if not target.exists():
            raise ArchiveError(self.tr("7-Zip did not output the expected file: {archive_name}").format(archive_name=archive_name))
        
        return target

    def _run_archive_command(self, args, cwd=None):
        p = subprocess.run(
            args, cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, errors="replace",
        )
        if p.returncode != 0:
            raise ArchiveError(p.stderr.strip() or self.tr("7-Zip Operation Failed"))
        return p

    # Set the compression level. Disable solid compression.
    def _compression_args(self, level: int):
        args = [f"-mx{level}"]
        if level != 0:
            args.append("-ms=off")
        return args

    # Update a file already in the 7z archive
    def update_one(self, archive_name: str, source: Path, level: int = 0):
        with tempfile.TemporaryDirectory(prefix="MTF7Z-update-") as td:
            staging_root = Path(td)
            staging = staging_root / archive_name
            staging.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, staging)
            self._run_archive_command(
                [SEVEN_Z, "u", "-y", *self._compression_args(level),
                 str(self.path), archive_name],
                cwd=staging_root,
            )

    # Add a new file or directory
    def add_one(self, archive_name: str, source: Path, level: int = 0):
        with tempfile.TemporaryDirectory(prefix="MTF7Z-add-") as td:
            staging_root = Path(td)

            staging = staging_root / archive_name
            staging.parent.mkdir(parents=True, exist_ok=True)

            if source.is_dir():
                shutil.copytree(source, staging)
            else:
                shutil.copy2(source, staging)

            self._run_archive_command(
                [SEVEN_Z, "a", "-y", *self._compression_args(level),
                 str(self.path), archive_name],
                cwd=staging_root,
            )


    def delete_one(self, archive_name: str):
        self._run_archive_command(
            [SEVEN_Z, "d", "-y", str(self.path), archive_name]
        )



class TempWorkspace:
    def __init__(self, archive_path: Path):
        self.archive_path = archive_path
        # The temp directory is in the same directory as the 7z archive.
        base = archive_path.parent
        self.path = Path(tempfile.mkdtemp(
            prefix=f"{archive_path.stem}.MTF7Z-",
            dir=str(base)
        ))

    def remove(self):
        if self.path.exists():
            shutil.rmtree(self.path, ignore_errors=False)


class MainWindow(QMainWindow):
    def __init__(self, settings, is_translation_loaded):
        super().__init__()
        self.settings = settings
        self.is_translation_loaded = is_translation_loaded

        self.archive = None
        self.workspace = None
        self.edited = {}
        self.archive_entries = {}

        self.setWindowTitle("MTF7Z")
        self.resize(900, 650)

        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["D", self.tr("File / Directory"), self.tr("Status")])
        self.tree.setTreePosition(1)
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.tree.header().setMinimumSectionSize(0)
        self.tree.setColumnWidth(0, 20)
        self.tree.setColumnWidth(1, 600)
        self.tree.setColumnWidth(2, 100)
        self.tree.itemDoubleClicked.connect(self.on_double_click)
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)
        self.tree.setFrameShape(QFrame.NoFrame)
        self.tree.setStyleSheet("QTreeWidget { background: white; border: none; }")

        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_frame.setStyleSheet(
            "QFrame#contentFrame { background: #ffffff; border: 1px solid #8a8f94; }"
        )
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(1, 1, 1, 1)
        content_layout.addWidget(self.tree)
        self.setCentralWidget(content_frame)
        self.setStyleSheet(
            "QMainWindow { background: #d9dcdf; }"
            "QToolBar { border-bottom: 1px solid #8a8f94; }"
            "QStatusBar { border-top: 1px solid #8a8f94; }"
        )

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("MTF7Z 0.8")

        self.make_actions()

        self.compression_combo.setCurrentIndex(self.settings.value("compression_level", 0, type=int))
        self.restoreGeometry(self.settings.value("geometry", b""))
        self.restoreState(self.settings.value("windowState", b""))


    def make_actions(self):
        toolbar = QToolBar()
        toolbar.setObjectName("Toolbar")
        self.addToolBar(toolbar)

        # Open a 7z archive
        open_action = QAction(self.tr("Open 7z"), self)
        open_action.triggered.connect(self.open_archive)
        open_action.setToolTip(self.tr("Open a 7z archive."))
        toolbar.addAction(open_action)

        # Edit files
        self.edit_action = QAction(self.tr("Edit"), self)
        self.edit_action.triggered.connect(self.edit_selected)
        self.edit_action.setEnabled(False)
        self.edit_action.setToolTip(self.tr("Open and edit selected files."))
        toolbar.addAction(self.edit_action)

        # Update changes
        self.update_action = QAction(self.tr("Update"), self)
        self.update_action.triggered.connect(self.check_and_update)
        self.update_action.setEnabled(False)
        self.update_action.setToolTip(self.tr("Apply changes to the 7z archive."))
        toolbar.addAction(self.update_action)

        # Extract files
        extract_action = QAction(self.tr("Extract"), self)
        extract_action.triggered.connect(self.extract_selected)
        self.extract_action = extract_action
        self.extract_action.setEnabled(False)
        self.extract_action.setToolTip(self.tr("Extract selected files to the temporary directory."))
        toolbar.addAction(extract_action)

        # Set compress level
        toolbar.addWidget(QLabel(self.tr("Compression Level:")))
        self.compression_combo = QComboBox()
        self.compression_combo.addItems([str(i) for i in range(10)])
        self.compression_combo.setCurrentIndex(0)
        self.compression_combo.setToolTip(self.tr("Compression level used when updating/adding files to the 7-Zip archive. 0 means store only."))
        toolbar.addWidget(self.compression_combo)

        # Refresh to check changes
        refresh_action = QAction(self.tr("Refresh"), self)
        refresh_action.triggered.connect(self.refresh_status)
        refresh_action.setToolTip(self.tr("Refresh to check for changes."))
        toolbar.addAction(refresh_action)

        # Close the 7z archive
        close_action = QAction(self.tr("Close 7z"), self)
        close_action.triggered.connect(self.close_archive)
        close_action.setToolTip(self.tr("Close the open 7z archive."))
        toolbar.addAction(close_action)

        # Choose languages
        language_button = QToolButton(self)
        language_button.setText(self.tr("Language"))
        language_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        language_menu = QMenu(self)
        language_button.setMenu(language_menu)

        self.language_actions = {}

        language_group = QActionGroup(self)
        language_group.setExclusive(True)

        for language, locale in [
            ("Deutsch", "de"),
            ("English", "en"),
            ("Español", "es"),
            ("Français", "fr"),
            ("Русский", "ru"),
            ("日本語", "ja"),
            ("简体中文", "zh_CN"),
            ("繁體中文", "zh_TW")
        ]:
            action = QAction(language, self)
            action.setCheckable(True)

            action.triggered.connect(
                lambda checked, locale=locale: self.change_language(locale)
            )

            language_group.addAction(action)
            language_menu.addAction(action)

            self.language_actions[locale] = action

        toolbar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )
        toolbar.addWidget(spacer)
        toolbar.addWidget(language_button)

        if self.is_translation_loaded:
            self.language_actions[self.settings.value("language", "en")].setChecked(True)
        else:
            self.language_actions["en"].setChecked(True)


    def change_language(self, locale):
        self.settings.setValue("language", locale)

        QMessageBox.information(
            self,
            self.tr("Language"),
            self.tr("The language will take effect after restarting the program.")
        )


    def open_archive(self):
        if self.archive:
            if not self.close_archive():
                return

        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Open 7z File"), "", "7-Zip archive (*.7z)"
        )
        if not path:
            return

        if not SEVEN_Z:
            QMessageBox.critical(
                self, self.tr("7-Zip Not Found"),
                self.tr("The 7z/7zz command was not found.\nPlease install 7-Zip first.")
            )
            return

        try:
            self.archive = Archive(Path(path).resolve())
            self.workspace = TempWorkspace(self.archive.path)
            self.edited.clear()
            self.archive_entries = {name: is_dir for name, is_dir in self.archive.list_files()}
            self.populate_tree(entries=list(self.archive_entries.items()))
            self.setWindowTitle(f"MTF7Z - {self.archive.path.name}")
            self.status.showMessage(str(self.archive.path))
        except Exception as e:
            self.archive = None
            if self.workspace:
                try:
                    self.workspace.remove()
                except Exception:
                    pass
            self.workspace = None
            self.archive_entries.clear()
            QMessageBox.critical(self, self.tr("Open Failed"), str(e))

    def populate_tree(self, entries=None):
        self.tree.clear()
        if entries is None:
            entries = list(self.archive_entries.items())

        root = self.tree.invisibleRootItem()
        dirs = {}

        for archive_name, is_dir in entries:
            parts = [p for p in archive_name.split("/") if p]
            parent = root
            accumulated = []

            for i, part in enumerate(parts):
                accumulated.append(part)
                key = "/".join(accumulated)

                if key not in dirs:
                    is_directory = i < len(parts) - 1 or is_dir

                    item = QTreeWidgetItem(
                        parent,
                        ["D" if is_directory else "", part, ""]
                    )
                    item.setData(1, Qt.UserRole, key)
                    item.setData(1, Qt.UserRole + 1, is_directory)
                    dirs[key] = item

                parent = dirs[key]

        for name in self.edited:
            self.update_tree_status(name)

        self.tree.expandToDepth(0)
        self.on_selection_changed()
        self.update_action.setEnabled(bool(self.edited))


    def compression_level(self):
        _compression_level = self.compression_combo.currentIndex()
        self.settings.setValue("compression_level", _compression_level)
        return _compression_level


    def is_text_or_image(self, path: Path):
        result = subprocess.run(
            ["file", "--mime-type", "-b", str(path)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False

        mime = result.stdout.strip()

        text_mimes = {
            "application/json", "application/xml", "application/javascript",
            "application/x-sh", "application/toml",
        }

        return (
            mime.startswith("text/")
            or mime.startswith("image/")
            or mime in text_mimes
        )


    def ensure_extracted(self, archive_name):
        if archive_name in self.edited and self.edited[archive_name].temp_path.exists():
            return self.edited[archive_name].temp_path

        target = self.archive.extract_one(
            archive_name,
            self.workspace.path,
        )

        self.edited[archive_name] = EditedFile(
            archive_name, target, file_signature(target), status=self.tr("Extracted")
        )
        
        self.update_tree_status(archive_name)
        self.update_action.setEnabled(True)
        return target


    def selected_archive_files(self):
        file_paths = []

        for item in self.tree.selectedItems():
            path = item.data(1, Qt.UserRole)

            if path and path in self.archive_entries:
                if not self.archive_entries[path]:
                    file_paths.append(path)

        return file_paths


    def extract_selected(self):
        file_paths = self.selected_archive_files()
        try:
            for archive_name in file_paths:
                self.ensure_extracted(archive_name)
                self.status.showMessage(self.tr("Extracted: {archive_name}").format(archive_name=archive_name))
        except Exception as e:
            QMessageBox.critical(self, self.tr("Extraction Failed"), str(e))


    def edit_selected(self):
        file_paths = self.selected_archive_files()
        directories_to_open = set()

        try:
            for archive_name in file_paths:
                temp_path = self.ensure_extracted(archive_name)
                if not temp_path:
                    continue

                if self.is_text_or_image(temp_path):
                    self.open_external(temp_path)
                else:
                    self.status.showMessage(self.tr("No external editor was found for this file type. Extracted only: {archive_name}").format(archive_name=archive_name))
                    directories_to_open.add(temp_path.parent)

                self.update_tree_status(archive_name)
            
            for directory in directories_to_open:
                self.open_external(directory)

            self.refresh_status()
        except Exception as e:
            QMessageBox.critical(self, self.tr("Edit/Extraction Failed"), str(e))


    def open_external(self, path: Path):
        try:
            # Use xdg-open.
            subprocess.Popen(["xdg-open", str(path)])
        except Exception as e:
            QMessageBox.warning(
                self, self.tr("Unable to open external editor"),
                self.tr(
                    "File was extracted to:\n{path}\n\n"
                    "but xdg-open could not be invoked:\n{e}"
                    ).format(path=path,e=e)
            )


    def on_double_click(self, item, column):
        self.edit_selected()


    def on_selection_changed(self):
        enabled = bool(self.selected_archive_files())
        self.edit_action.setEnabled(enabled)
        self.extract_action.setEnabled(enabled)


    def update_tree_status(self, archive_name):
        it = self.find_item(archive_name)
        if not it:
            return
        state = self.edited.get(archive_name)
        if not state:
            it.setText(2, "")
        elif not state.temp_path.exists():
            it.setText(2, self.tr("Temporary File Deleted"))
        elif state.modified():
            it.setText(2, self.tr("Modified, Pending Update"))
        else:
            it.setText(2, state.status)

    def find_item(self, path):
        it = self.tree.invisibleRootItem()
        parts = path.split("/")
        for part in parts:
            found = None
            for i in range(it.childCount()):
                c = it.child(i)
                if c.text(1) == part:
                    found = c
                    break
            if found is None:
                return None
            it = found
        return it


    def scan_temp_entries(self):
        found = {}
        if not self.workspace or not self.workspace.path.exists():
            return found

        for p in self.workspace.path.rglob("*"):
            rel = p.relative_to(self.workspace.path).as_posix()
            found[rel] = p

        return found


    def temp_state_changes(self):
        temp_entries = self.scan_temp_entries()
        changes = []

        # Files that were extracted/edited and then deleted.
        for name, state in self.edited.items():
            if not state.temp_path.exists():
                changes.append(("deleted", name, state))

        # New files manually placed into the workspace.
        known = set(self.edited) | set(self.archive_entries)

        new_entries = []
        for rel, path in temp_entries.items():
            if rel not in known:
                new_entries.append((rel, path))

        new_entries.sort(key=lambda x: (x[0].count("/"), x[0]))

        reported = []
        for rel, path in new_entries:
            if any(
                rel == parent or rel.startswith(parent + "/")
                for parent in reported
            ):
                continue

            reported.append(rel)
            changes.append(("new", rel, path))

        # Modified extracted files.
        for name, state in self.edited.items():
            if state.temp_path.exists() and state.modified():
                changes.append(("modified", name, state))

        return changes


    def refresh_status(self):
        if not self.archive:
            return
        changes = self.temp_state_changes()

        if len(changes) > 0:
            self.update_action.setEnabled(True)
        else:
            self.update_action.setEnabled(False)
        
        for name in self.edited:
            self.update_tree_status(name)
        self.status.showMessage(
            self.tr(
                "Extracted/edited {counts_edited} file(s).  "
                "Found {counts_changes} changes in the temporary directory."
                ).format(counts_edited=len(self.edited), counts_changes=len(changes))
        )


    def process_temp_changes(self, interactive=True):
        changes = self.temp_state_changes()
        if not changes:
            return True

        for kind, name, obj in changes:
            if kind == "deleted":
                answer = QMessageBox.question(
                    self, self.tr("Temporary File Not Found"),
                    self.tr(
                        "The file in the temporary directory has been deleted:\n{name}\n\n"
                        "Delete the corresponding file from the 7z archive as well?"
                        ).format(name=name),
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.Yes
                )
                if answer == QMessageBox.Cancel:
                    return False
                if answer == QMessageBox.Yes:
                    try:
                        self.archive.delete_one(name)
                        del self.edited[name]
                        self.archive_entries.pop(name, None)
                    except Exception as e:
                        QMessageBox.critical(self, self.tr("Deletion Failed"), self.tr("Failed to delete {name}:\n\n{e}").format(name=name, e=e))
                        return False
                else:
                    # Keep the state so the user can decide later.
                    continue

            elif kind == "new":
                _type = self.tr("File") if not obj.is_dir() else self.tr("Directory")
                answer = QMessageBox.question(
                    self, self.tr("New {_type} Found").format(_type=_type),
                    self.tr(
                        "A new {_type} not present in the 7z archive was found in the temporary directory:\n{name}\n\n"
                        "Add it to the 7z archive?"
                        ).format(_type=_type, name=name),
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.Yes
                )
                if answer == QMessageBox.Cancel:
                    return False
                if answer == QMessageBox.Yes:
                    try:
                        self.archive.add_one(name, obj, self.compression_level())
                  
                        if not obj.is_dir():
                            sig = file_signature(obj)
                            self.edited[name] = EditedFile(name, obj, sig, status=self.tr("Extracted"))
                            self.archive_entries[name] = False
                        else:
                            self.archive_entries = {
                                name: is_dir
                                for name, is_dir in self.archive.list_files()
                            }

                            for p in obj.rglob("*"):
                                if not p.is_file():
                                    continue

                                rel = p.relative_to(self.workspace.path).as_posix()
                                sig = file_signature(p)

                                self.edited[rel] = EditedFile(rel, p, sig, status=self.tr("Extracted"))

                    except Exception as e:
                        QMessageBox.critical(self, self.tr("Add Failed"), self.tr("Failed to add {name}:\n\n{e}").format(name=name, e=e))
                        return False
                else:
                    continue

            elif kind == "modified":
                state = obj
                answer = QMessageBox.question(
                    self, self.tr("File Modified"),
                    self.tr("File:\n{name}\n\nThe temporary file has been modified.\nUpdate the 7z archive?").format(name=name),
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.Yes
                )
                if answer == QMessageBox.Cancel:
                    return False
                if answer == QMessageBox.Yes:
                    try:
                        self.archive.update_one(name, state.temp_path, self.compression_level())
                        state.original_signature = file_signature(state.temp_path)
                        state.updated_signature = state.original_signature
                        state.status = self.tr("Extracted")
                    except Exception as e:
                        QMessageBox.critical(self, self.tr("Update Failed"), self.tr("Failed to update {name}:\n\n{e}").format(name=name, e=e))
                        return False

            self.update_tree_status(name)

        self.populate_tree()
        return True


    def save_expanded_paths(self):
        paths = set()

        def walk(item):
            for i in range(item.childCount()):
                child = item.child(i)
                path = child.data(1, Qt.UserRole)

                if child.isExpanded() and path:
                    paths.add(path)

                walk(child)

        walk(self.tree.invisibleRootItem())
        return paths


    def restore_expanded_paths(self, paths):
        def walk(item):
            for i in range(item.childCount()):
                child = item.child(i)
                path = child.data(1, Qt.UserRole)

                if path in paths:
                    child.setExpanded(True)

                walk(child)

        walk(self.tree.invisibleRootItem())


    # Apply changes to the 7z archive. Preserve the expanded levels of the directory tree.
    def check_and_update(self):
        if not self.archive:
            return
        
        expanded_paths = self.save_expanded_paths()
        self.process_temp_changes(interactive=True)
        self.refresh_status()
        self.restore_expanded_paths(expanded_paths)


    def close_archive(self):
        if not self.archive:
            return True

        # Perform a complete check before closing. If the user cancels at any step, keep the workspace.
        if not self.process_temp_changes(interactive=True):
            return False
      
        # If the user selects 'No' when prompted to delete/add items, they will remain in the temporary directory.
        # Remind the user explicitly again when closing to avoid silently losing them.
        remaining = self.temp_state_changes()
        if remaining:
            names = "\n".join(f"• {name}" for _, name, _ in remaining)
            answer = QMessageBox.question(
                self, self.tr("Unprocessed Changes Remain"),
                self.tr(
                    "The following items have not yet been updated to the 7z archive:\n\n{names}\n\n"
                    "The temporary directory will be deleted when the archive is closed, and these changes will be lost. Continue closing?"
                    ).format(names=names),
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if answer == QMessageBox.No:
                return False

        try:
            self.workspace.remove()
        except Exception as e:
            QMessageBox.warning(
                self, self.tr("Cleanup Failed"),
                self.tr(
                    "Unable to delete the temporary directory:\n{_path}\n\n{e}\n\n"
                    "To prevent loss of changes, this 7z archive will remain open."
                    ).format(_path=self.workspace.path, e=e)
            )
            return False

        self.archive = None
        self.workspace = None
        self.edited.clear()
        self.archive_entries.clear()
        self.tree.clear()
        self.edit_action.setEnabled(False)
        self.update_action.setEnabled(False)
        self.extract_action.setEnabled(False)
        self.setWindowTitle("MTF7Z")
        self.status.showMessage(self.tr("No 7z Archive Open"))
        return True

    def closeEvent(self, event):
        if self.close_archive():
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)

    settings = QSettings("MTF7Z", "MTF7Z_config")
    # Load language
    locale = settings.value("language", "en")

    translator = QTranslator()
    is_translation_loaded = translator.load("translations/mtf7z_{locale}.qm".format(locale=locale))
    if not is_translation_loaded and locale != "en":
        QMessageBox.warning(
            None, "MTF7Z",
            QCoreApplication.translate(
                "Startup",
                "Failed to load translation."
            )
        )
        settings.setValue("language", "en")

    app.installTranslator(translator)

    app.setApplicationName("MTF7Z")

    if not SEVEN_Z:
        QMessageBox.warning(
            None, "MTF7Z",
            QCoreApplication.translate(
                "Startup",
                "7z/7zz was not found at startup.\n"
                "Install 7-Zip to use this feature."
            )
        )

    w = MainWindow(
        settings,
        is_translation_loaded
        )
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
