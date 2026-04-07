import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

st.title("Utility Corridor Planning Tool")

# ---------------------------
# 🔹 Road Inputs
# ---------------------------
st.sidebar.header("Road Inputs")

road_length = st.sidebar.number_input("Road Length (m)", value=10.0)
road_margin = st.sidebar.number_input("Road Margin (m)", value=0.0)

offset_type = st.sidebar.selectbox(
    "Offset Reference",
    ["Left", "Center", "Right"]
)

# ---------------------------
# 🔹 Road Sections
# ---------------------------
st.subheader("Road Sections")

sections = st.text_area(
    "Define Sections (start,end,name) one per line",
    "0,1.5,Walkway\n1.5,6,Pavement\n6,10,Sidewalk"
)

section_data = []
for line in sections.split("\n"):
    try:
        s, e, name = line.split(",")
        section_data.append((float(s), float(e), name))
    except:
        pass

# ---------------------------
# 🔹 Utilities Input
# ---------------------------
st.subheader("Utilities")

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Utility": ["EL"],
        "Width": [1.0],
        "Margin": [0.0],
        "Start": [0.0],
        "Clash Allowed": [True]
    })

df = st.data_editor(st.session_state.data, num_rows="dynamic")

# ---------------------------
# 🔹 Calculation Logic
# ---------------------------
results = []
prev_right = 0
prev_margin = 0

for i, row in df.iterrows():
    width = row["Width"]
    margin = row["Margin"]
    start = row["Start"]

    if i == 0:
        left = start
        center = left + width / 2
        right = left + width
        clash = 0
    else:
        overlap = min(prev_margin, margin)

        left = prev_right - overlap
        center = left + width / 2
        right = left + width
        clash = overlap

    # Clash check
    clash_flag = False
    if i > 0:
        allowed = min(prev_margin, margin)
        actual_overlap = prev_right - left
        if actual_overlap > allowed:
            clash_flag = True

    # Offset conversion
    if offset_type == "Center":
        offset = center - road_length / 2
    elif offset_type == "Right":
        offset = road_length - center
    else:
        offset = center

    results.append({
        "Utility": row["Utility"],
        "Width": width,
        "Margin": margin,
        "Center Offset": round(offset, 2),
        "Left": round(left, 2),
        "Right": round(right, 2),
        "Clash Used": round(clash, 2),
        "Clash": "YES" if clash_flag else "NO"
    })

    prev_right = right
    prev_margin = margin

result_df = pd.DataFrame(results)

# ---------------------------
# 🔹 Output Table
# ---------------------------
st.subheader("Results")
st.dataframe(result_df, use_container_width=True)

# ---------------------------
# 🔹 Visualization
# ---------------------------
st.subheader("Road Visualization")

for r in results:
    st.markdown(
        f"""
        <div style="position:relative; height:30px; margin-bottom:5px; background:#eee;">
            <div style="
                position:absolute;
                left:{(r['Left']/road_length)*100}%;
                width:{((r['Right']-r['Left'])/road_length)*100}%;
                height:100%;
                background:#4CAF50;">
            </div>
            <span style="position:absolute; left:5px; font-size:12px;">
                {r['Utility']}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------
# 🔹 Export
# ---------------------------
st.subheader("Export")

csv = result_df.to_csv(index=False).encode("utf-8")
st.download_button("Download Excel (CSV)", csv, "utility_layout.csv", "text/csv")

# ---------------------------
# 🔹 Validation
# ---------------------------
total_used = result_df["Right"].max()

if total_used > road_length:
    st.error(f"⚠️ تجاوز road length! Used: {total_used} m")
else:
    st.success(f"✅ Total Used: {total_used} m / {road_length} m")
