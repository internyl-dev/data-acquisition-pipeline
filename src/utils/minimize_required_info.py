
from src.models import QueueItem, Fields

def minimize_required_info(queue_item:QueueItem, all_target_info:list) -> None:
    """
    Minimizes the target fields of a queue item to only the information that's needed
    even if the target fields specified extra info
    """
    target_fields = queue_item.target_fields

    for target_info in all_target_info:
        if isinstance(target_info, str) and isinstance(target_fields[0], Fields):
            all_target_info[all_target_info.index(target_info)] = Fields(target_info)
        elif isinstance(target_info, Fields) and isinstance(target_fields[0], str):
            all_target_info[all_target_info.index(target_info)] = target_info.value

    queue_item.target_fields = list(set(target_fields) & set(all_target_info))

if __name__ == "__main__":
    item = QueueItem("gamer.com", ["overview", "eligibility"])
    all_target_info = ["overview"]
    minimize_required_info(item, all_target_info)
    print(item.target_fields)

    item = QueueItem("gamer.com", ["overview"])
    all_target_info = ["overview", "eligibility"]
    minimize_required_info(item, all_target_info)
    print(item.target_fields)

    item = QueueItem("gamer.com", ["overview", "eligibility"])
    all_target_info = [Fields.OVERVIEW]
    minimize_required_info(item, all_target_info)
    print(item.target_fields)

    item = QueueItem("gamer.com", [Fields.OVERVIEW, Fields.ELIGIBILITY])
    all_target_info = ["overview"]
    minimize_required_info(item, all_target_info)
    print(item.target_fields)