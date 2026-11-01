// Abstract Factory: a trait with an associated type per product, so a family is
// chosen once, statically, and mixing families is a compile error.
trait Connection {
    fn describe(&self) -> String;
}
trait Migration {
    fn sql(&self) -> String;
}

trait DbFactory {
    type Conn: Connection;
    type Mig: Migration;
    fn connect(&self, url: &str) -> Self::Conn;
    fn migration(&self, table: &str) -> Self::Mig;
}

struct PgConn(String);
struct PgMigration(String);
struct SqliteConn(String);
struct SqliteMigration(String);

impl Connection for PgConn {
    fn describe(&self) -> String {
        format!("postgres at {}", self.0)
    }
}
impl Migration for PgMigration {
    fn sql(&self) -> String {
        format!("CREATE TABLE {} (id BIGSERIAL PRIMARY KEY)", self.0)
    }
}
impl Connection for SqliteConn {
    fn describe(&self) -> String {
        format!("sqlite at {}", self.0)
    }
}
impl Migration for SqliteMigration {
    fn sql(&self) -> String {
        format!("CREATE TABLE {} (id INTEGER PRIMARY KEY)", self.0)
    }
}

struct Postgres;
struct Sqlite;

impl DbFactory for Postgres {
    type Conn = PgConn;
    type Mig = PgMigration;
    fn connect(&self, url: &str) -> PgConn {
        PgConn(url.into())
    }
    fn migration(&self, table: &str) -> PgMigration {
        PgMigration(table.into())
    }
}
impl DbFactory for Sqlite {
    type Conn = SqliteConn;
    type Mig = SqliteMigration;
    fn connect(&self, url: &str) -> SqliteConn {
        SqliteConn(url.into())
    }
    fn migration(&self, table: &str) -> SqliteMigration {
        SqliteMigration(table.into())
    }
}

fn bootstrap<F: DbFactory>(factory: &F, url: &str) {
    let conn = factory.connect(url);
    let mig = factory.migration("orders");
    println!("{} -> {}", conn.describe(), mig.sql());
}

fn main() {
    bootstrap(&Postgres, "db.prod:5432");
    bootstrap(&Sqlite, "local.db");
}
