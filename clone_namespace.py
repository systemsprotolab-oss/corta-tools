from sqlalchemy import create_engine
from sqlalchemy.engine.interfaces import DBAPICursor
from corta_classes import (
    Namespace,
    Module,
    ModuleField,
    Page,
    PageLayout,
    Record,
    RecordRevision,
)

NS_ID = 427425760141246465
DB_URL = "<DB_URL>"

TARGET_DB_URL = (
    "<TARGET_DB_URL>"
)


def connect_db(dsn: str):
    return create_engine(
        dsn,
    ).raw_connection()


def get_namespace(cur: DBAPICursor) -> Namespace:
    print("mapping namespace....")
    query = """
        SELECT id, slug, enabled, meta, name, created_at, updated_at, deleted_at
        FROM compose_namespace
        WHERE id = %s 
    """
    cur.execute(query, (NS_ID,))
    row = cur.fetchone()
    if not row:
        raise Exception("Namespace not found")
    ns = Namespace()
    ns.ns_id = row[0]
    ns.slug = row[1]
    ns.enabled = row[2]
    ns.meta = row[3]
    ns.name = row[4]
    ns.created_at = row[5]
    ns.updated_at = row[6]
    ns.deleted_at = row[7]
    return ns


def rel_module(cur: DBAPICursor, namespace_id: int) -> list[Module]:
    print("mapping modules....")
    query = """
        SELECT id, rel_namespace, handle, name, meta, config, created_at, updated_at, deleted_at
        FROM compose_module
        WHERE rel_namespace = %s 
    """
    cur.execute(query, (namespace_id,))
    rows = cur.fetchall()
    modules = []
    for row in rows:
        mod = Module()
        mod.module_id = row[0]
        mod.rel_namespace = row[1]
        mod.handle = row[2]
        mod.name = row[3]
        mod.meta = row[4]
        mod.config = row[5]
        mod.created_at = row[6]
        mod.updated_at = row[7]
        mod.deleted_at = row[8]
        modules.append(mod)
    return modules


def rel_module_fields(cur: DBAPICursor, module_id: int) -> list[ModuleField]:
    print("mapping module fields....")
    query = """
        SELECT id, rel_module, place, kind, options, name, label, config,
        is_required, is_multi, default_value,
        created_at, updated_at, deleted_at
        FROM compose_module_field
        WHERE rel_module = %s 
    """
    cur.execute(query, (module_id,))
    rows = cur.fetchall()
    module_fields = []
    for row in rows:
        mf = ModuleField()
        mf.id = row[0]
        mf.rel_module = row[1]
        mf.place = row[2]
        mf.kind = row[3]
        mf.options = row[4]
        mf.name = row[5]
        mf.label = row[6]
        mf.config = row[7]
        mf.is_required = row[8]
        mf.is_multi = row[9]
        mf.default_value = row[10]
        mf.created_at = row[11]
        mf.updated_at = row[12]
        mf.deletad_at = row[13]

        module_fields.append(mf)
    return module_fields


def rel_module_pages(cur: DBAPICursor, module_id: int) -> list[Page]:
    print("mapping modules....")
    query = """
        SELECT id, rel_namespace, title, handle, self_id, rel_module,
        meta, config, blocks, visible, weight,
        description, created_at, updated_at, deleted_at
        FROM compose_page
        WHERE rel_module = %s 
    """
    cur.execute(query, (module_id,))
    rows = cur.fetchall()
    pages = []
    for row in rows:
        page = Page()
        page.id = row[0]
        page.rel_namespace = row[1]
        page.title = row[2]
        page.handle = row[3]
        page.self_id = row[4]
        page.rel_module = row[5]
        page.meta = row[6]
        page.config = row[7]
        page.blocks = row[8]
        page.visible = row[9]
        page.weight = row[10]
        page.description = row[11]
        page.created_at = row[12]
        page.updated_at = row[13]
        page.deleted_at = row[14]

        pages.append(page)
    return pages


def rel_page_layouts(cur: DBAPICursor, page_id: int) -> list[PageLayout]:
    print("mapping page layouts....")
    query = """
        SELECT id, handle, page_id, parent_id, rel_namespace,
        weight, meta, config, blocks, owned_by,
        created_at, updated_at, deleted_at
        FROM compose_page_layout
        WHERE page_id = %s 
    """
    cur.execute(query, (page_id,))
    rows = cur.fetchall()
    layouts = []
    for row in rows:
        layout = PageLayout()
        layout.id = row[0]
        layout.handle = row[1]
        layout.page_id = row[2]
        layout.parent_id = row[3]
        layout.rel_namespace = row[4]
        layout.weight = row[5]
        layout.meta = row[6]
        layout.config = row[7]
        layout.blocks = row[8]
        layout.owned_by = row[9]
        layout.created_at = row[10]
        layout.updated_at = row[11]
        layout.deleted_at = row[12]

        layouts.append(layout)
    return layouts


def rel_records(cur: DBAPICursor, module_id: int) -> list[Record]:
    print("mapping records....")
    query = """
        SELECT id, revision, rel_module, values, created_at, updated_at, deleted_at
        FROM compose_record
        WHERE rel_module = %s 
    """
    cur.execute(query, (module_id,))
    rows = cur.fetchall()
    records = []
    for row in rows:
        record = Record()
        record.id = row[0]
        record.revision = row[1]
        record.rel_module = row[2]
        record.values = row[3]
        record.created_at = row[4]
        record.updated_at = row[5]
        record.deleted_at = row[6]

        records.append(record)
    return records


def rel_records_revisions(cur: DBAPICursor, resource_id: int):
    print("mapping revisions....")
    query = """
    SELECT id, ts, revision, revision, operation,
    rel_user, delta 
    FROM compose_record_revisions 
    WHERE rel_resource = %s
    """
    cur.execute(query, (resource_id,))
    rows = cur.fetchall()
    for row in rows:
        revision = RecordRevision()
        revision.id = row[0]
        revision.ts = row[1]
        revision.revision = row[2]
        revision.operation = row[3]
        revision.rel_user = row[4]
        revision.delta = row[5]


def map_namespace():
    conn = connect_db(DB_URL)
    try:
        cur = conn.cursor()
        ns = get_namespace(cur=cur)
        ns.modules = rel_module(cur=cur, namespace_id=ns.ns_id)

        for mod in ns.modules:
            mod.fields = rel_module_fields(cur=cur, module_id=mod.module_id)
            mod.records = rel_records(cur=cur, module_id=mod.module_id)
            mod.pages = rel_module_pages(cur=cur, module_id=mod.module_id)
            for page in mod.pages:
                page.layouts = rel_page_layouts(cur=cur, page_id=page.id)
            # for record in mod.records:
            #     record.revision = rel_records_revisions(cur=cur, resource_id=record.id)

    finally:
        conn.close()

    return ns


ns = map_namespace()
print(ns)

conn = connect_db(TARGET_DB_URL)
try:
    cur = conn.cursor()
    query = """INSERT INTO compose_namespace id, slug, enabled, meta, name, created_at, updated_at, deleted_at VALUES
    (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cur.execute(
        query,
        (ns.ns_id, ns.slug, ns.enabled, ns.meta, ns.name, ns.created_at, ns.updated_at),
    )
    conn.commit()
finally:
    conn.close()
# TODO добавить выгрузку Атачментов
