import re

# 从 @test/对话记录 - 神经内镜有哪些主流的厂商？ (2).md 中复制的真实测试数据
test_data = """
References:
[^1]: [2023年神经内窥镜市场十大领先企业 - Emergen Research](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGgP7Hz8H6ILTG8ETqLw968tua9k5BhTYBG5IYyfm10ZghxaAVPQ2ajvHjIvTnXy1MQllGCs_9j59eQ2P4wm88dEiq-szGyDXf0-ecHJZQuc95vVkBorovEGr83FvwwboQV_XQz8Ioah3Vg7Sz_ymd2ayblstz2EKGXLGrNL7tQpIFlvKzeSwSsjhe3E6aztLlTCJBhiY2iAWZY_Jjj6etU)
[^2]: [Neuroendoscopy Companies - Top Company List - Mordor Intelligence](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHGpZ3Q1sVFJ0tEV7SDH1Fo8eOdiL3RQoValPPVVd4BIM092_h8CFaIq17LcXTP25QmcAERyR926n3gLeXXwqaemQ1Rw-8q-gUIOolUCY-GYlxQy5WGviHXBKlmRIgIgrl-be0DG9tutiQyJjniIO1w2Guh_jHEewzfpxbpjLhju6RV8v3YPYm41iI0MNt4)
[^3]: [Top 6 companies Dominating the Neuroendoscopy Devices Market Globally in 2025](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEjLRgIuIJ-J_d6UrDs2zxo6I82Qe18fTzVyX2sJPw-lN4q40SDUh6pPK3SekWDh5zCd05scFI2USWSvRqZ4ytYakumHyr9gRnV4UAu_h6dyFqZInM4ftkXvG7lyvxLf4k-IPUyfioSglQdkFl0ITuiLhy1lpggvzfs-R7eSV0qL5PBxbr8ff5O3oc5kFLXSnfQnxMHkSplFgzo4iOmdsCaJYPwEkW3)
"""

# 新的、为匹配 [^N]: [Title](URL) 格式而设计的正则表达式
# 它会捕获三个组：(数字, 标题, URL)
regex = r'\[\^(\d+)\]:\s*\[([^\]]+)\]\(([^)]+)\)'

# 执行查找
found_references = re.findall(regex, test_data)

# 打印结果以供验证
print("--- Regex Test Results ---")
if found_references:
    print(f"Successfully found {len(found_references)} references.")
    for i, ref in enumerate(found_references):
        print(f"  Match {i+1}:")
        print(f"    Index: {ref[0]}")
        print(f"    Title: {ref[1]}")
        print(f"    URL:   {ref[2]}")
else:
    print("No references found. The regex is incorrect.")

print("--- End of Test ---")
