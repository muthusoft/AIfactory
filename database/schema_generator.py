"""
Dynamic database schema generator.

Generates database schemas based on project requirements.
This is the AI that designs the database for the product being built.
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Column:
    """Represents a database column."""
    name: str
    type: str  # string, integer, float, boolean, datetime, json, text
    nullable: bool = True
    unique: bool = False
    indexed: bool = False
    primary_key: bool = False
    foreign_key: Optional[str] = None  # "table.column"
    description: Optional[str] = None
    default: Optional[Any] = None


@dataclass
class Table:
    """Represents a database table."""
    name: str
    description: str
    columns: List[Column]
    relationships: List[Dict[str, Any]] = None
    indexes: List[List[str]] = None
    
    def __post_init__(self):
        if self.relationships is None:
            self.relationships = []
        if self.indexes is None:
            self.indexes = []


@dataclass
class DatabaseSchema:
    """Complete database schema for a project."""
    project_name: str
    description: str
    tables: List[Table]
    version: int = 1
    created_at: str = ""
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "project_name": self.project_name,
            "description": self.description,
            "version": self.version,
            "created_at": self.created_at,
            "notes": self.notes,
            "tables": [
                {
                    "name": t.name,
                    "description": t.description,
                    "columns": [
                        {
                            "name": c.name,
                            "type": c.type,
                            "nullable": c.nullable,
                            "unique": c.unique,
                            "indexed": c.indexed,
                            "primary_key": c.primary_key,
                            "foreign_key": c.foreign_key,
                            "description": c.description,
                            "default": c.default,
                        }
                        for c in t.columns
                    ],
                    "relationships": t.relationships,
                    "indexes": t.indexes,
                }
                for t in self.tables
            ]
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DatabaseSchema":
        """Create from dictionary."""
        tables = []
        for t_data in data.get("tables", []):
            columns = [
                Column(
                    name=c["name"],
                    type=c["type"],
                    nullable=c.get("nullable", True),
                    unique=c.get("unique", False),
                    indexed=c.get("indexed", False),
                    primary_key=c.get("primary_key", False),
                    foreign_key=c.get("foreign_key"),
                    description=c.get("description"),
                    default=c.get("default"),
                )
                for c in t_data.get("columns", [])
            ]
            
            table = Table(
                name=t_data["name"],
                description=t_data.get("description", ""),
                columns=columns,
                relationships=t_data.get("relationships", []),
                indexes=t_data.get("indexes", []),
            )
            tables.append(table)
        
        return DatabaseSchema(
            project_name=data["project_name"],
            description=data.get("description", ""),
            tables=tables,
            version=data.get("version", 1),
            created_at=data.get("created_at", ""),
            notes=data.get("notes", ""),
        )


class SchemaGenerator:
    """Generates database schemas from requirements."""
    
    def __init__(self):
        """Initialize schema generator."""
        self.generated_schemas: Dict[str, DatabaseSchema] = {}
    
    def example_todo_app_schema(self) -> DatabaseSchema:
        """Example: Generate schema for a todo app."""
        return DatabaseSchema(
            project_name="todo-app",
            description="Schema for a task management application",
            tables=[
                Table(
                    name="users",
                    description="User accounts",
                    columns=[
                        Column(name="id", type="integer", primary_key=True),
                        Column(name="email", type="string", unique=True, indexed=True),
                        Column(name="username", type="string", unique=True),
                        Column(name="password_hash", type="text"),
                        Column(name="created_at", type="datetime"),
                        Column(name="updated_at", type="datetime"),
                    ],
                ),
                Table(
                    name="todos",
                    description="Todo items",
                    columns=[
                        Column(name="id", type="integer", primary_key=True),
                        Column(name="user_id", type="integer", foreign_key="users.id"),
                        Column(name="title", type="string", indexed=True),
                        Column(name="description", type="text"),
                        Column(name="category", type="string"),
                        Column(name="completed", type="boolean", default=False),
                        Column(name="due_date", type="datetime"),
                        Column(name="priority", type="string"),
                        Column(name="created_at", type="datetime"),
                        Column(name="updated_at", type="datetime"),
                    ],
                    relationships=[
                        {"type": "many-to-one", "related_table": "users", "foreign_key": "user_id"}
                    ],
                    indexes=[
                        ["user_id", "completed"],
                        ["user_id", "created_at"],
                    ],
                ),
                Table(
                    name="categories",
                    description="Todo categories",
                    columns=[
                        Column(name="id", type="integer", primary_key=True),
                        Column(name="user_id", type="integer", foreign_key="users.id"),
                        Column(name="name", type="string"),
                        Column(name="color", type="string"),
                        Column(name="created_at", type="datetime"),
                    ],
                    relationships=[
                        {"type": "many-to-one", "related_table": "users", "foreign_key": "user_id"}
                    ],
                ),
            ],
            notes="Schema includes users, todos, and categories. Supports authentication and task categorization.",
        )
    
    def example_ecommerce_schema(self) -> DatabaseSchema:
        """Example: Generate schema for an e-commerce platform."""
        return DatabaseSchema(
            project_name="ecommerce-platform",
            description="Schema for an e-commerce platform",
            tables=[
                Table(
                    name="users",
                    description="User accounts",
                    columns=[
                        Column(name="id", type="integer", primary_key=True),
                        Column(name="email", type="string", unique=True, indexed=True),
                        Column(name="name", type="string"),
                        Column(name="password_hash", type="text"),
                        Column(name="role", type="string", default="customer"),
                        Column(name="created_at", type="datetime"),
                    ],
                ),
                Table(
                    name="products",
                    description="Product catalog",
                    columns=[
                        Column(name="id", type="integer", primary_key=True),
                        Column(name="name", type="string", indexed=True),
                        Column(name="description", type="text"),
                        Column(name="price", type="float"),
                        Column(name="stock", type="integer"),
                        Column(name="category", type="string", indexed=True),
                        Column(name="image_url", type="string"),
                        Column(name="created_at", type="datetime"),
                    ],
                ),
                Table(
                    name="orders",
                    description="Customer orders",
                    columns=[
                        Column(name="id", type="integer", primary_key=True),
                        Column(name="user_id", type="integer", foreign_key="users.id"),
                        Column(name="total_price", type="float"),
                        Column(name="status", type="string", default="pending"),
                        Column(name="payment_method", type="string"),
                        Column(name="created_at", type="datetime"),
                    ],
                    relationships=[
                        {"type": "many-to-one", "related_table": "users", "foreign_key": "user_id"}
                    ],
                ),
                Table(
                    name="order_items",
                    description="Items in orders",
                    columns=[
                        Column(name="id", type="integer", primary_key=True),
                        Column(name="order_id", type="integer", foreign_key="orders.id"),
                        Column(name="product_id", type="integer", foreign_key="products.id"),
                        Column(name="quantity", type="integer"),
                        Column(name="price", type="float"),
                    ],
                    relationships=[
                        {"type": "many-to-one", "related_table": "orders", "foreign_key": "order_id"},
                        {"type": "many-to-one", "related_table": "products", "foreign_key": "product_id"},
                    ],
                ),
            ],
            notes="Schema includes users, products, orders, and order items. Supports e-commerce operations.",
        )
    
    def generate_sql_script(self, schema: DatabaseSchema) -> str:
        """
        Generate SQLite CREATE TABLE statements.
        
        Args:
            schema: Database schema
        
        Returns:
            SQL script
        """
        statements = []
        
        for table in schema.tables:
            # Build CREATE TABLE statement
            column_defs = []
            
            for col in table.columns:
                col_def = f"{col.name} {self._map_type_to_sql(col.type)}"
                
                if col.primary_key:
                    col_def += " PRIMARY KEY"
                elif not col.nullable:
                    col_def += " NOT NULL"
                
                if col.unique:
                    col_def += " UNIQUE"
                
                if col.default is not None:
                    col_def += f" DEFAULT {col.default}"
                
                if col.foreign_key:
                    col_def += f" REFERENCES {col.foreign_key}"
                
                column_defs.append(col_def)
            
            # Create table statement
            create_stmt = f"""
CREATE TABLE {table.name} (
    {', '.join(column_defs)}
);
"""
            statements.append(create_stmt)
            
            # Add indexes
            for idx_cols in table.indexes:
                idx_name = f"idx_{table.name}_{'_'.join(idx_cols)}"
                idx_stmt = f"CREATE INDEX {idx_name} ON {table.name} ({', '.join(idx_cols)});"
                statements.append(idx_stmt)
        
        return "\n".join(statements)
    
    @staticmethod
    def _map_type_to_sql(col_type: str) -> str:
        """Map Python type to SQLite type."""
        type_map = {
            "string": "TEXT",
            "integer": "INTEGER",
            "float": "REAL",
            "boolean": "BOOLEAN",
            "datetime": "DATETIME",
            "json": "JSON",
            "text": "TEXT",
        }
        return type_map.get(col_type, "TEXT")
    
    def save_schema(self, schema: DatabaseSchema, path: str) -> None:
        """Save schema to JSON file."""
        with open(path, 'w') as f:
            json.dump(schema.to_dict(), f, indent=2)
        logger.info(f"Schema saved to {path}")
    
    def load_schema(self, path: str) -> DatabaseSchema:
        """Load schema from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        schema = DatabaseSchema.from_dict(data)
        logger.info(f"Schema loaded from {path}")
        return schema
