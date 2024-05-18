import csv
from collections import defaultdict, deque
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def read_people(filename):
    people = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            people.append((row['Roll Number'], row['Department']))
    return people

def read_rooms(filename):
    rooms = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            room_capacity = int(row['Rows']) * int(row['Cols'])
            rooms.append((row['Room Number'], int(row['Rows']), int(row['Cols']), room_capacity))
    return rooms

def generate_seating_chart(people, rooms):
    # Group people by department
    departments = defaultdict(deque)
    for person, department in people:
        departments[department].append(person)

    department_list = sorted(departments.keys())

    all_people = []
    while any(departments.values()):
        for dept in department_list:
            if departments[dept]:
                all_people.append(departments[dept].popleft())

    seating_chart = []
    room_index = 0
    current_room = []
    room_capacity = rooms[room_index][3]

    for person in all_people:
        current_room.append(person)
        if len(current_room) == room_capacity:
            seating_chart.append((rooms[room_index][0], rooms[room_index][1], rooms[room_index][2], current_room))
            current_room = []
            room_index += 1
            if room_index < len(rooms):
                room_capacity = rooms[room_index][3]
            else:
                room_capacity = float('inf')  # No more rooms available

    if current_room:
        seating_chart.append((rooms[room_index][0], rooms[room_index][1], rooms[room_index][2], current_room))

    return seating_chart

def create_pdf(seating_chart, filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    page_width, page_height = letter
    margin = 72  # 1-inch margin on all sides
    usable_width = page_width - 2 * margin

    for room, rows, cols, occupants in seating_chart:
        elements.append(Paragraph(f"{room}", styles['Title']))
        grid_data = [["" for _ in range(cols)] for _ in range(rows)]
        index = 0
        for r in range(rows):
            for c in range(cols):
                if index < len(occupants):
                    grid_data[r][c] = occupants[index]
                    index += 1
                else:
                    break

        # Calculate column width
        col_width = usable_width / cols

        table = Table(grid_data, colWidths=[col_width] * cols)
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.whitesmoke),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    doc.build(elements)

# Reading input data
people = read_people('people.csv')
rooms = read_rooms('rooms.csv')

# Generating the seating chart
seating_chart = generate_seating_chart(people, rooms)

# Creating the PDF
create_pdf(seating_chart, "seating_chart.pdf")
