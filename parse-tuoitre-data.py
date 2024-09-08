import requests
from bs4 import BeautifulSoup
import json

def parse_url(url):
    # Tải nội dung HTML từ URL sử dụng requests
    try:
        response = requests.get(url)
        response.raise_for_status()  # Kiểm tra lỗi HTTP
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

    html_content = response.text
    doc_content = ""

    # Sử dụng BeautifulSoup để parse nội dung HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Lấy tiêu đề từ thẻ <h1> với class là 'article-title'
    h1_tag = soup.find('h1', class_='article-title')
    if h1_tag:
        h1_tag = h1_tag.get_text(strip=True)
        doc_content += h1_tag + "\n"
    else:
        h1_tag = ""

    # Lấy nội dung từ các thẻ <p> và các thẻ tiêu đề khác (h2, h3)
    content_section = soup.find('div', class_='detail-content')
    if content_section:
        for element in content_section.find_all(['h2', 'h3', 'p', 'ul']):
            if element.name in ['h2', 'h3']:
                doc_content += element.get_text(strip=True) + "\n"
            elif element.name == 'p':
                doc_content += element.get_text(strip=True) + "\n"
            elif element.name == 'ul':
                li_tags = element.find_all('li')
                for li_tag in li_tags:
                    doc_content += f"- {li_tag.get_text(strip=True)}" + "\n"

    # Trích xuất thông tin từ thẻ <meta> với name là 'description'
    meta_tag = soup.find('meta', attrs={'name': 'description'})
    span_tag_text = ""
    if meta_tag:
        span_tag_text = meta_tag.get('content', '').strip()

    # Lấy category từ thẻ <div class="detail-cate">
    category_tag = soup.find('div', class_='detail-cate')
    category = ""
    if category_tag:
        category_link = category_tag.find('a')
        if category_link:
            category = category_link.get_text(strip=True)

    # Tạo cấu trúc JSON từ dữ liệu đã trích xuất
    data = {
        "url": url,  # Đường dẫn URL
        "content": doc_content.strip(),
        "category": category,
        "title": h1_tag
    }

    return data


output_file = 'all_data.json'
input_file = 'urls.json'

# Load the all_urls list from the JSON file
with open(input_file, 'r', encoding='utf-8') as file:
    all_urls = json.load(file)

data_urls = []

# Giả sử `all_urls` là danh sách các từ điển với khóa 'url'
subset_data = all_urls[0:]  # Lấy một số lượng nhỏ để kiểm tra
for item in subset_data:
    url = item.get("url")  # Sử dụng `get` để tránh lỗi nếu không có khóa
    if url:
        data_urls.append(url)

print(f"All URLs loaded from {data_urls}")

all_data = []

for url in data_urls:
    data = parse_url(url)
    print(data)
    if data and data.get('content'):  # Chỉ thêm dữ liệu hợp lệ
        all_data.append(data)

# Lưu tất cả dữ liệu vào một tệp JSON duy nhất
with open(output_file, 'w', encoding='utf-8') as json_file:
    json.dump(all_data, json_file, ensure_ascii=False, indent=4)

print(f"Data has been saved to {output_file}")

