"""
android_agent.storage.bytecode

SQLite storage for detailed DEX bytecode data.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class BytecodeStore:
    """Store and query detailed DEX bytecode data."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

        self._create_schema()

    def _create_schema(self) -> None:
        """Create the SQLite database schema."""

        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS dex_files (
                id INTEGER PRIMARY KEY,
                jar_name TEXT NOT NULL,
                dex_name TEXT NOT NULL,
                size INTEGER,
                compressed_size INTEGER
            );

            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY,
                dex_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                superclass TEXT,
                access TEXT,
                FOREIGN KEY (dex_id)
                    REFERENCES dex_files(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS class_interfaces (
                class_id INTEGER NOT NULL,
                interface TEXT NOT NULL,
                FOREIGN KEY (class_id)
                    REFERENCES classes(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS methods (
                id INTEGER PRIMARY KEY,
                class_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                descriptor TEXT,
                access TEXT,
                FOREIGN KEY (class_id)
                    REFERENCES classes(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS instructions (
                id INTEGER PRIMARY KEY,
                method_id INTEGER NOT NULL,
                offset INTEGER NOT NULL,
                opcode TEXT NOT NULL,
                output TEXT,
                FOREIGN KEY (method_id)
                    REFERENCES methods(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS method_calls (
                id INTEGER PRIMARY KEY,
                caller_method_id INTEGER NOT NULL,
                target_class TEXT NOT NULL,
                target_method TEXT NOT NULL,
                target_descriptor TEXT NOT NULL,
                opcode TEXT NOT NULL,
                FOREIGN KEY (caller_method_id)
                    REFERENCES methods(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_classes_dex_id
                ON classes(dex_id);

            CREATE INDEX IF NOT EXISTS idx_classes_name
                ON classes(name);

            CREATE INDEX IF NOT EXISTS idx_methods_class_id
                ON methods(class_id);

            CREATE INDEX IF NOT EXISTS idx_methods_name
                ON methods(name);

            CREATE INDEX IF NOT EXISTS idx_instructions_method_id
                ON instructions(method_id);

            CREATE INDEX IF NOT EXISTS idx_instructions_opcode
                ON instructions(opcode);

            CREATE INDEX IF NOT EXISTS idx_instructions_method_offset
                ON instructions(method_id, offset);

            CREATE INDEX IF NOT EXISTS idx_method_calls_caller
                ON method_calls(caller_method_id);

            CREATE INDEX IF NOT EXISTS idx_method_calls_target
                ON method_calls(
                    target_class,
                    target_method,
                    target_descriptor
                );
            """
        )

        self.connection.commit()

    # ------------------------------------------------------------------
    # Insert methods
    # ------------------------------------------------------------------

    def add_dex_file(
        self,
        jar_name: str,
        dex_name: str,
        size: int,
        compressed_size: int,
    ) -> int:
        """Add a DEX file and return its database ID."""

        cursor = self.connection.execute(
            """
            INSERT INTO dex_files (
                jar_name,
                dex_name,
                size,
                compressed_size
            )
            VALUES (?, ?, ?, ?)
            """,
            (jar_name, dex_name, size, compressed_size),
        )

        return cursor.lastrowid

    def add_class(
        self,
        dex_id: int,
        name: str,
        superclass: str | None,
        access: str,
    ) -> int:
        """Add a class and return its database ID."""

        cursor = self.connection.execute(
            """
            INSERT INTO classes (
                dex_id,
                name,
                superclass,
                access
            )
            VALUES (?, ?, ?, ?)
            """,
            (dex_id, name, superclass, access),
        )

        return cursor.lastrowid

    def add_class_interface(
        self,
        class_id: int,
        interface: str,
    ) -> None:
        """Add an interface implemented by a class."""

        self.connection.execute(
            """
            INSERT INTO class_interfaces (
                class_id,
                interface
            )
            VALUES (?, ?)
            """,
            (class_id, interface),
        )

    def add_method(
        self,
        class_id: int,
        name: str,
        descriptor: str,
        access: str,
    ) -> int:
        """Add a method and return its database ID."""

        cursor = self.connection.execute(
            """
            INSERT INTO methods (
                class_id,
                name,
                descriptor,
                access
            )
            VALUES (?, ?, ?, ?)
            """,
            (class_id, name, descriptor, access),
        )

        return cursor.lastrowid

    def add_instruction(
        self,
        method_id: int,
        offset: int,
        opcode: str,
        output: str,
    ) -> int:
        """Add an instruction and return its database ID."""

        cursor = self.connection.execute(
            """
            INSERT INTO instructions (
                method_id,
                offset,
                opcode,
                output
            )
            VALUES (?, ?, ?, ?)
            """,
            (method_id, offset, opcode, output),
        )

        return cursor.lastrowid

    def add_method_call(
        self,
        caller_method_id: int,
        target_class: str,
        target_method: str,
        target_descriptor: str,
        opcode: str,
    ) -> int:
        """Add a method call relationship and return its database ID."""

        cursor = self.connection.execute(
            """
            INSERT INTO method_calls (
                caller_method_id,
                target_class,
                target_method,
                target_descriptor,
                opcode
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                caller_method_id,
                target_class,
                target_method,
                target_descriptor,
                opcode,
            ),
        )

        return cursor.lastrowid

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    def find_classes(
        self,
        name: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Find classes whose names contain the supplied text."""

        rows = self.connection.execute(
            """
            SELECT
                c.id,
                c.dex_id,
                c.name,
                c.superclass,
                c.access,
                d.jar_name,
                d.dex_name
            FROM classes AS c
            JOIN dex_files AS d
                ON d.id = c.dex_id
            WHERE c.name LIKE ?
            ORDER BY c.name
            LIMIT ?
            """,
            (f"%{name}%", limit),
        ).fetchall()

        return [dict(row) for row in rows]

    def get_class(
        self,
        class_id: int,
    ) -> dict[str, Any] | None:
        """Return a class and its interfaces."""

        row = self.connection.execute(
            """
            SELECT
                c.id,
                c.dex_id,
                c.name,
                c.superclass,
                c.access,
                d.jar_name,
                d.dex_name
            FROM classes AS c
            JOIN dex_files AS d
                ON d.id = c.dex_id
            WHERE c.id = ?
            """,
            (class_id,),
        ).fetchone()

        if row is None:
            return None

        result = dict(row)

        interfaces = self.connection.execute(
            """
            SELECT interface
            FROM class_interfaces
            WHERE class_id = ?
            ORDER BY interface
            """,
            (class_id,),
        ).fetchall()

        result["interfaces"] = [row["interface"] for row in interfaces]

        return result

    def find_methods(
        self,
        name: str,
        limit: int = 50,
        class_name: str | None = None,
        descriptor: str | None = None,
    ) -> list[dict[str, Any]]:
        """Find methods by name, optionally restricted by class and descriptor."""

        query = """
            SELECT
                m.id,
                m.class_id,
                m.name,
                m.descriptor,
                m.access,
                c.name AS class_name
            FROM methods AS m
            JOIN classes AS c
                ON c.id = m.class_id
            WHERE m.name LIKE ?
        """

        parameters: list[Any] = [f"%{name}%"]

        if class_name is not None:
            query += """
                AND c.name = ?
            """
            parameters.append(class_name)

        if descriptor is not None:
            query += """
                AND m.descriptor = ?
            """
            parameters.append(descriptor)

        query += """
            ORDER BY c.name, m.name, m.descriptor
            LIMIT ?
        """

        parameters.append(limit)

        rows = self.connection.execute(
            query,
            parameters,
        ).fetchall()

        return [dict(row) for row in rows]

    def get_instructions(
        self,
        method_id: int,
    ) -> list[dict[str, Any]]:
        """Return all instructions belonging to a method."""

        rows = self.connection.execute(
            """
            SELECT
                id,
                method_id,
                offset,
                opcode,
                output
            FROM instructions
            WHERE method_id = ?
            ORDER BY offset
            """,
            (method_id,),
        ).fetchall()

        return [dict(row) for row in rows]

    def get_method_calls(
        self,
        method_id: int,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return methods called by a method."""

        rows = self.connection.execute(
            """
            SELECT
                id,
                caller_method_id,
                target_class,
                target_method,
                target_descriptor,
                opcode
            FROM method_calls
            WHERE caller_method_id = ?
            ORDER BY id
            LIMIT ?
            """,
            (method_id, limit),
        ).fetchall()

        return [dict(row) for row in rows]

    def find_method_callers(
            self,
            target_class: str,
            target_method: str,
            target_descriptor: str,
            limit: int = 50,
        ) -> list[dict[str, Any]]:
            """Find methods that call the specified method."""

            rows = self.connection.execute(
                """
            SELECT
                mc.id,
                mc.caller_method_id,
                mc.target_class,
                mc.target_method,
                mc.target_descriptor,
                mc.opcode,
                m.name AS caller_method,
                m.descriptor AS caller_descriptor,
                c.name AS caller_class
            FROM method_calls AS mc
            JOIN methods AS m
                ON m.id = mc.caller_method_id
            JOIN classes AS c
                ON c.id = m.class_id
            WHERE mc.target_class = ?
                AND mc.target_method = ?
                AND mc.target_descriptor = ?
            ORDER BY mc.id
            LIMIT ?
            """,
                (
                    target_class,
                    target_method,
                    target_descriptor,
                    limit,
                ),
            ).fetchall()

            return [dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Transaction / lifecycle methods
    # ------------------------------------------------------------------

    def commit(self) -> None:
        """Commit pending database changes."""

        self.connection.commit()

    def close(self) -> None:
        """Commit and close the database connection."""

        self.connection.commit()
        self.connection.close()
