
import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.title("薪資計算器")

file_path = "salary_records.csv"
if not os.path.exists(file_path):
    df = pd.DataFrame(columns=[
        "姓名", "月份", "月薪", "病假天數", "平日加班時數", 
        "國定假日加班時數", "國定假日名稱", "獎金", "勞保", "健保", "實領薪資"
    ])
    df.to_csv(file_path, index=False)

with st.form("salary_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("姓名", value="")
        month = st.selectbox("月份", [f"{datetime.now().year}-{m:02}" for m in range(1, 13)], index=datetime.now().month - 1)
    with col2:
        base_salary = st.number_input("月薪", value=0)
        bonus = st.number_input("獎金", value=0.0)

    sick_leave_days = st.number_input("病假天數（半薪）", value=0.0)

    st.markdown("#### ⏱ 工時與加班")
    total_work_hours = st.number_input("本月實際工作總時數", value=0.0)
    base_hours = 40 * 4  # 以一週 40 小時、4 週為標準：160 小時
    overtime_hours = max(0.0, total_work_hours - base_hours)

    st.markdown("#### 📅 國定假日出勤薪資")
    holiday_name = st.text_input("國定假日名稱（可留空）", value="")
    holiday_hours = st.number_input("當月國定假日出勤總時數", value=0.0)

    auto_insurance = st.checkbox("自動計算勞健保（36,000 級距）", value=True)
    if auto_insurance:
        labor_insurance = 908
        health_insurance = 563
    else:
        labor_insurance = st.number_input("勞保（自付）", value=0.0)
        health_insurance = st.number_input("健保（自付）", value=0.0)

    submitted = st.form_submit_button("📥 計算並儲存")

if submitted:
    daily_salary = base_salary / 30
    hourly_salary = daily_salary / 8
    sick_deduction = sick_leave_days * daily_salary * 0.5
    overtime_pay = overtime_hours * hourly_salary * 1.33
    holiday_pay = holiday_hours * hourly_salary

    gross = base_salary - sick_deduction + overtime_pay + holiday_pay + bonus
    net = gross - labor_insurance - health_insurance

    st.markdown("## 📄 薪資明細")
    st.write(f"病假扣薪　　　　：- {sick_deduction:.0f} 元")
    st.write(f"平日加班費　　　：+ {overtime_pay:.0f} 元（本月總工時 {total_work_hours}）")
    if holiday_hours > 0:
        st.write(f"國定假日加班費　：+ {holiday_pay:.0f} 元（{holiday_hours} 小時 × 1 倍時薪）")
    st.write(f"獎金　　　　　　：+ {bonus:.0f} 元")
    st.write(f"勞保　　　　　　：- {labor_insurance:.0f} 元")
    st.write(f"健保　　　　　　：- {health_insurance:.0f} 元")
    st.success(f"實領薪資　　　　：{net:.0f} 元")

    # 儲存紀錄
    df = pd.read_csv(file_path)
    new_row = {
        "姓名": name,
        "月份": month,
        "月薪": base_salary,
        "病假天數": sick_leave_days,
        "平日加班時數": overtime_hours,
        "國定假日加班時數": holiday_hours,
        "國定假日名稱": holiday_name,
        "獎金": bonus,
        "勞保": labor_insurance,
        "健保": health_insurance,
        "實領薪資": round(net, 0)
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(file_path, index=False)
    st.success("✅ 薪資紀錄已儲存！")

st.markdown("---")
st.subheader("📑 歷史薪資紀錄")
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📤 下載紀錄 CSV", csv, "salary_records.csv", "text/csv")
