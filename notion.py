import requests
import json
from datetime import datetime

NOTION_TOKEN = "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"  # 你的Integration Token
TASK_DATABASE_ID = "7f6b2f6c54834800af03f20c23509c1f"  # Task数据库 ID
IDEA_DATABASE_ID = "21562a58d3af80459b11cb3c64987f92"  # 灵感收藏夹 ID
NOTION_VERSION = "2022-06-28"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION,
}


def create_idea(content, ptype , create_date, status="未处理"):
    print("start create_task")

    url = "https://api.notion.com/v1/pages"

    properties = {
        "内容": {
            "title": [
                {
                    "text": {"content": content}
                }
            ]
        }
    }

    # 只有 status 有值时才加进去
    if status:
        properties["状态"] = {
            "select": {"name": status}
        }

    # 只有 status 有值时才加进去
    if ptype:
        properties["类型"] = {
            "select": {"name": ptype}
        }

    # 只有 due_date 有值才加进去
    if create_date:
        properties["创建日期"] = {
            "date": {"start": create_date}
        }



    payload = {
        "parent": {"database_id": IDEA_DATABASE_ID},
        "properties": properties
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        print("HTTP status code:", response.status_code)

        # 成功
        if response.status_code == 200:
            print("✅ Task created successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print("❌ Failed to create task.")
            print("Response body:")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print("⚠️ Request error:", e)


def create_task(name, status, tags=None, catalog_group=None, catalog=None, due_date=None):
    print("start create_task")

    url = "https://api.notion.com/v1/pages"

    properties = {
        "Task name": {
            "title": [
                {
                    "text": {"content": name}
                }
            ]
        }
    }

    # 只有 status 有值时才加进去
    if status:
        properties["Status"] = {
            "status": {"name": status}
        }

    # 只有 due_date 有值才加进去
    if due_date:
        properties["计划完成日期"] = {
            "date": {"start": due_date}
        }

    # Tags 是列表，有内容才加进去
    if tags:
        properties["标签"] = {
            "multi_select": [{"name": tag} for tag in tags]
        }

    if catalog_group:
        properties["分组"] = {
            "select": {"name": catalog_group}
        }

    if catalog:
        properties["小分组"] = {
            "select": {"name": catalog}
        }

    payload = {
        "parent": {"database_id": TASK_DATABASE_ID},
        "properties": properties
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        print("HTTP status code:", response.status_code)

        # 成功
        if response.status_code == 200:
            print("✅ Task created successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print("❌ Failed to create task.")
            print("Response body:")
            print(response.text)

    except requests.exceptions.RequestException as e:
        print("⚠️ Request error:", e)


def main():
    # create_task(
    #     name="Write Notion API Guide",
    #     status="Not Started",
    #     # tags=["API", "Documentation"],
    #     # catalog_group="catalog_group",
    #     # catalog="catalog",
    #     # due_date=datetime.today().strftime('%Y-%m-%d'),
    # )

    create_idea(
        content="first idea",
        ptype="灵感",
        create_date=datetime.today().strftime('%Y-%m-%d')
    )

if __name__ == '__main__':
    main()
