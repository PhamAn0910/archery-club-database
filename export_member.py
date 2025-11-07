import pymysql

# Update these with your actual DB credentials
conn = pymysql.connect(
    host='localhost',
    user='your_user',
    password='your_password',
    database='archery_db'
)

with conn.cursor() as cursor:
    cursor.execute("SELECT av_number, full_name, birth_year, gender_id, division_id, is_recorder FROM club_member")
    rows = cursor.fetchall()

print("-- Exported club_member data")
print("INSERT INTO club_member (av_number, full_name, birth_year, gender_id, division_id, is_recorder) VALUES")
values = []
for row in rows:
    av_number, full_name, birth_year, gender_id, division_id, is_recorder = row
    values.append(f"('{av_number}', '{full_name.replace(\"'\", \"''\")}', {birth_year}, {gender_id}, {division_id}, {int(is_recorder)})")
print(",\n".join(values) + ";")

conn.close()