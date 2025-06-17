import pandas as pd # type: ignore
from openpyxl import load_workbook # type: ignore
import re

def unhide_columns(excel_path, sheet_name):
    wb = load_workbook(excel_path)
    ws = wb[sheet_name]
    for col in ws.column_dimensions:
        ws.column_dimensions[col].hidden = False
    wb.save(excel_path)

def extract_percentage(sob_data, pattern):
    for i, row in sob_data.iterrows():
        match = re.search(pattern, str(row.iloc[0]))
        if match:
            percentage_text = str(row.iloc[-1])
            percentage_value = pd.to_numeric(percentage_text.replace('%', '').strip(), errors='coerce')
            return percentage_value
    return None

def extract_stoploss_data(sob_data, sob_coinsurance_value1):
    stoploss_threshold_pattern = r"On the first \$([0-9,]+) per Calendar Year"
    threshold, smaller_percentage, larger_percentage = None, sob_coinsurance_value1, 1
    for i, row in sob_data.iterrows():
        threshold_match = re.search(stoploss_threshold_pattern, str(row.iloc[0]))
        if threshold_match:
            threshold = int(threshold_match.group(1).replace(",", ""))
        if threshold and smaller_percentage and larger_percentage:
            break
    if threshold is None or smaller_percentage is None or larger_percentage is None:
        raise ValueError("Could not find stoploss data in the SOB sheet.")
    return threshold, smaller_percentage, larger_percentage

def compare_rbl_with_local_Caribbean(local_data, sob_data):
    rbl_rows = local_data[local_data['Benefit Type'] == 'RBL ']
    for index, row in rbl_rows.iterrows():
        local_per_service1 = pd.to_numeric(row['Per Service'], errors='coerce')
        break  # Break the loop after the first match
    return local_per_service1

def compare_rbo_with_overseas(local_data,sob_data):
    rbo_rows = local_data[local_data['Benefit Type'] == 'RBO ']   
    for index, row in rbo_rows.iterrows():
        local_per_service2 = pd.to_numeric(row['Per Service'], errors ='coerce')
        break  # Break the loop after the first match
    return local_per_service2

def compare_ev_with_local_Caribbean(local_data, sob_data):
    ev_rows = local_data[local_data['Benefit Type'] == "EV  "]
    for index, row in ev_rows.iterrows():
        local_per_service3 =pd.to_numeric(row['Per Service'], errors='coerce')
        break  # Break the loop after the first match
    return local_per_service3

def compare_nurd_with_local(local_data, sob_data):
    nurd_rows = local_data[local_data['Benefit Type'] == "NURD"]
    for index, row in nurd_rows.iterrows():
        local_per_service4 = pd.to_numeric(row['Per Service'], errors="coerce")   
        break  # Break the loop after the first match
    return local_per_service4

def compare_nurn_with_local(local_data, sob_data):
    nurn_rows = local_data[local_data['Benefit Type'] == "NURN"]
    for index, row in nurn_rows.iterrows():
        local_per_service5 = pd.to_numeric(row['Per Service'], errors="coerce")    
    return local_per_service5

def compare_nuhn_with_local(local_data, sob_data):
    nuhn_rows = local_data[local_data['Benefit Type'] == "NUHN"]
    for index, row in nuhn_rows.iterrows():
        local_per_service6 = pd.to_numeric(row['Per Service'], errors="coerce")   
    return local_per_service6

def compare_ov_with_local(local_data, sob_data):
    ov_rows = local_data[local_data['Benefit Description'] == "OFFICE VISIT             "]
    local_per_service7 = None
    for index, row in ov_rows.iterrows():
        local_per_service7 = pd.to_numeric(row['Per Service'], errors="coerce")
    return local_per_service7

def compare_tov_with_local(local_data, sob_data):
    tov_rows = local_data[local_data['Benefit Description'] == "TELEMEDICINE OFFICE VISIT"]
    local_per_service11 = None
    for index, row in tov_rows.iterrows():
        local_per_service11 = pd.to_numeric(row['Per Service'], errors="coerce")
    return local_per_service11

def compare_homv_with_local(local_data, sob_data):
    homv_rows = local_data[local_data['Benefit Description'] == "HOME VISIT               "]
    local_per_service8 = None
    for index, row in homv_rows.iterrows():
        local_per_service8 = pd.to_numeric(row['Per Service'], errors="coerce")
    return local_per_service8

def compare_hosv_with_local(local_data, sob_data):
    hosv_rows = local_data[local_data['Benefit Description'] == "HOSPITAL VISIT           "]
    local_per_service9 = None
    for index, row in hosv_rows.iterrows():
        local_per_service9 = pd.to_numeric(row['Per Service'], errors="coerce")
    return local_per_service9

def compare_sv_with_local(local_data, sob_data):
    sv_rows = local_data[local_data['Benefit Description'] == "SPECIALIST VISIT         "]
    local_per_service10 = None
    for index, row in sv_rows.iterrows():
        local_per_service10 = pd.to_numeric(row['Per Service'], errors="coerce")
    return local_per_service10



def compare_local_with_sob(local_data, sob_data,user_input):
  
    major_max_text = "For Active Employees under age 65" if user_input == 'yes' else "For Active Employees age 65 & over and Retirees"
    sob_major_max_row = sob_data[sob_data.iloc[:, 0].str.contains(major_max_text, na=False, case=False)]
    if sob_major_max_row.empty:
        raise ValueError(f'Could not find "{major_max_text}" in the SOB sheet.')
    sob_major_max_value = pd.to_numeric(sob_major_max_row.iloc[0, -1], errors='coerce')
    #print(sob_major_max_value)

    benefit_types = ['ANES', 'ASUR', 'CHRT', 'DXL ', 'HAEM', 'HS  ','ICU ', 'MISC', 'RX  ', 'SURG', 'GAMB', 'CHIR', 'NUT ', 'OT ', 'OTP ', 'POD ', 'PT  ', 'ST ', 'RBL ','RBO ','EV  ','NURD','NURN','NUHN','OV  ','HOMV','HOSV','SV  ','TOV ']
    benefit_types1 = ['CHIR', 'NUT ', 'OT  ', 'OTP ', 'POD ', 'PT  ', 'ST  ' ]

    sob_deductible_text = "Per Each Individual Insured"
    sob_deductible_row = sob_data[sob_data.iloc[:, 0].str.contains(sob_deductible_text, na=False, case=False)]
    if sob_deductible_row.empty:
        raise ValueError(f'Could not find "{sob_deductible_text}" in the SOB sheet.')
    sob_deductible_value = pd.to_numeric(sob_deductible_row.iloc[0, -1], errors='coerce')

    sob_int_chir_text = 'Physiotherapy and other Health-care Professional Groups - Maximum Allowable Expense'
    sob_int_chir_row = sob_data[sob_data.iloc[:, 0].str.contains(sob_int_chir_text, na=False, case=False)]
    if sob_int_chir_row.empty:
        raise ValueError(f'Could not find "{sob_int_chir_text}" in the SOB sheet.')
    sob_int_chir_value = pd.to_numeric(sob_int_chir_row.iloc[0, -1], errors='coerce')

    sob_familydeductible_text = "Per Family"
    sob_familydeductible_row = sob_data[sob_data.iloc[:, 0].str.contains(sob_familydeductible_text, na=False, case=False)]
    if sob_familydeductible_row.empty:
        raise ValueError(f'Could not find "{sob_familydeductible_text}" in the SOB sheet.')
    sob_familydeductible_value = pd.to_numeric(sob_familydeductible_row.iloc[0, -1], errors='coerce') * sob_deductible_value

    sob_int_rbl_text = r'Local\s*\(Caribbean|Caricom\)'
    sob_int_rbl_row = sob_data[sob_data.iloc[:, 0].str.contains(sob_int_rbl_text, na=False, case=False)]
    if sob_int_rbl_row.empty:
        raise ValueError(f'Could not find "{sob_int_rbl_text}" in the SOB sheet.')
    sob_int_rbl_value = pd.to_numeric(sob_int_rbl_row.iloc[0, -1], errors='coerce')

    sob_int_rbo_text = r'Overseas\s*\(Non-Caribbean|Non-Caricom\)'
    sob_int_rbo_row = sob_data[sob_data.iloc[:,0].str.contains(sob_int_rbo_text, na=False, case=False)]
    if sob_int_rbo_row.empty:
        raise ValueError(f'Could not find "{sob_int_rbo_text}" in the SOB sheet.')
    sob_int_rbo_value =pd.to_numeric(sob_int_rbo_row.iloc[0,-1], errors= 'coerce')

    sob_int_ev_text =r'Emergency Doctor’s Visits Benefit\s*\(Home and Hospital\)'
    sob_int_ev_row = sob_data[sob_data.iloc[:,0].str.contains(sob_int_ev_text, na=False, case=False)]
    if sob_int_ev_row.empty:
        raise ValueError(f'Could not find"{sob_int_ev_text}" in the SOB sheet.')
    sob_int_ev_value= pd.to_numeric(sob_int_ev_row.iloc[0,-2], errors ='coerce')
    if pd.isnull(sob_int_ev_value):
        sob_int_ev_value = pd.to_numeric(sob_int_ev_row.iloc[0,-1], errors ='coerce')

    sob_int_nurd_text = r'Maximum per 8-hour Shift – In private residence\s*\(Day\)'
    sob_int_nurd_row = sob_data[sob_data.iloc[0:,0].str.contains(sob_int_nurd_text, na= False, case= False)]
    if sob_int_nurd_row.empty:
        raise ValueError(f'Could not find"{sob_int_nurd_text}" in the SOB sheet.')
    sob_int_nurd_value = pd.to_numeric(sob_int_nurd_row.iloc[0,-1], errors='coerce') /8

    sob_int_nurn_text =  r'Maximum per 8-hour Shift – In private residence\s*\(Night\)'
    sob_int_nurn_row = sob_data[sob_data.iloc[0:,0].str.contains(sob_int_nurn_text, na= False, case= False)]
    if sob_int_nurn_row.empty:
        raise ValueError(f'Could not find"{sob_int_nurn_text}" in the SOB sheet.')
    sob_int_nurn_value = pd.to_numeric(sob_int_nurn_row.iloc[0,-1], errors='coerce') /8

    sob_int_nuhn_text =  r'Maximum per 8-hour Shift – In hospital\s*\(Night\)'
    sob_int_nuhn_row = sob_data[sob_data.iloc[0:,0].str.contains(sob_int_nuhn_text, na= False, case= False)]
    if sob_int_nuhn_row.empty:
        raise ValueError(f'Could not find"{sob_int_nuhn_text}" in the SOB sheet.')
    sob_int_nuhn_value = pd.to_numeric(sob_int_nuhn_row.iloc[0,-1], errors='coerce') /8

    sob_int_ov_text =  "Office Visit"
    sob_int_ov_row = sob_data[sob_data.iloc[0:,0].str.contains(sob_int_ov_text, na= False, case= False)]
    if sob_int_ov_row.empty:
        raise ValueError(f'Could not find"{sob_int_ov_text}" in the SOB sheet.')
    sob_int_ov_value = pd.to_numeric(sob_int_ov_row.iloc[0,-2], errors='coerce')
    if pd.isnull(sob_int_ov_value):
        sob_int_ov_value = pd.to_numeric(sob_int_ov_row.iloc[0,-1], errors='coerce')


    sob_int_homv_text =  "Home Visit"
    sob_int_homv_row = sob_data[sob_data.iloc[0:,0].str.contains(sob_int_homv_text, na= False, case= False)]
    if sob_int_homv_row.empty:
        raise ValueError(f'Could not find"{sob_int_homv_text}" in the SOB sheet.')
    sob_int_homv_value = pd.to_numeric(sob_int_homv_row.iloc[0,-2], errors='coerce')
    if pd.isnull(sob_int_homv_value):
        sob_int_homv_value = pd.to_numeric(sob_int_homv_row.iloc[0,-1], errors='coerce')


    sob_int_hosv_text =  "Hospital Visit"
    sob_int_hosv_row = sob_data[sob_data.iloc[0:,0].str.contains(sob_int_hosv_text, na= False, case= False)]
    if sob_int_hosv_row.empty:
        raise ValueError(f'Could not find"{sob_int_hosv_text}" in the SOB sheet.')
    sob_int_hosv_value = pd.to_numeric(sob_int_hosv_row.iloc[0,-2], errors='coerce')
    if pd.isnull(sob_int_hosv_value):
        sob_int_hosv_value =pd.to_numeric(sob_int_hosv_row.iloc[0,-1], errors ='coerce')

    sob_int_sv_text =  "Specialist Visit by Referral Only"
    sob_int_sv_row = sob_data[sob_data.iloc[0:,0].str.contains(sob_int_sv_text, na= False, case= False)]
    if sob_int_sv_row.empty:
        raise ValueError(f'Could not find"{sob_int_sv_text}" in the SOB sheet.')
    sob_int_sv_value = pd.to_numeric(sob_int_sv_row.iloc[0,-2], errors='coerce')
    if pd.isnull(sob_int_sv_value):
        sob_int_sv_value = pd.to_numeric(sob_int_sv_row.iloc[0,-1], errors='coerce')

    
    coinsurance_pattern = r"On the first \$[0-9,]+ per Calendar Year"
    sob_coinsurance_value = extract_percentage(sob_data, coinsurance_pattern) * 100
    sob_coinsurance_value1 = sob_coinsurance_value / 100
    if sob_coinsurance_value is None:
        raise ValueError(f'Could not find coinsurance pattern "{coinsurance_pattern}" in the SOB sheet.')

    threshold, smaller_percentage, larger_percentage = extract_stoploss_data(sob_data, sob_coinsurance_value1)

    for benefit_list, description in [(benefit_types, "general comparison"), (benefit_types1, "physiotherapy")]:
        benefit_rows = local_data[(local_data['Benefit Type'].isin(benefit_list)) & (local_data['Sub-Category'] == 'S') & (local_data['Type'] .isin([1, 2]) )]

        for index, row in benefit_rows.iterrows():
            local_deductible = pd.to_numeric(row['Individual Deductible'], errors='coerce')
            local_family_deductible = pd.to_numeric(row['Family Deductible'], errors='coerce')
            local_medicalCOin = pd.to_numeric(row['Major Medical  % 1'], errors='coerce')
            local_major_max = pd.to_numeric(row['Major/Base Dollar Max'], errors='coerce')
            local_stoploss = pd.to_numeric(row['STOPLOSS'], errors='coerce')

            comments = []

            if row['Benefit Type'] == 'RBL ':
                local_per_service1 = compare_rbl_with_local_Caribbean(local_data, sob_data)
                if local_per_service1 != sob_int_rbl_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_rbl_value} INSTEAD OF {local_per_service1}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")

            elif row['Benefit Type'] == 'RBO ':
                local_per_service2 = compare_rbo_with_overseas(local_data, sob_data)
                if local_per_service2 != sob_int_rbo_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_rbo_value} INSTEAD OF {local_per_service2}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")

            elif row['Benefit Type'] == 'EV  ':
                local_per_service3 = compare_ev_with_local_Caribbean(local_data, sob_data)
                if local_per_service3 != sob_int_ev_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_ev_value} INSTEAD OF {local_per_service3}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")

            elif row['Benefit Type'] == 'NURD':
                local_per_service4 = compare_nurd_with_local(local_data, sob_data)
                if local_per_service4 != sob_int_nurd_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_nurd_value} INSTEAD OF {local_per_service4}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")

            elif row['Benefit Type'] == "NURN":
                local_per_service5 = compare_nurn_with_local(local_data, sob_data)
                if local_per_service5 != sob_int_nurn_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_nurn_value} INSTEAD OF {local_per_service5}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")

            elif row['Benefit Type'] == "NUHN":
                local_per_service6 = compare_nuhn_with_local(local_data, sob_data)
                if local_per_service6 != sob_int_nuhn_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_nuhn_value} INSTEAD OF {local_per_service6}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")

            elif row['Benefit Type'] == "OV  ":
                local_per_service7 = compare_ov_with_local(local_data, sob_data)
                if local_per_service7 != sob_int_ov_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_ov_value} INSTEAD OF {local_per_service7}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")
            
            elif row['Benefit Type'] == "TOV ":
                local_per_service11 = compare_tov_with_local(local_data, sob_data)
                if local_per_service11 != sob_int_ov_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_ov_value} INSTEAD OF {local_per_service11}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")
            
            elif row['Benefit Type'] == "HOMV":
                local_per_service8 = compare_homv_with_local(local_data, sob_data)
                if local_per_service8 != sob_int_homv_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_homv_value} INSTEAD OF {local_per_service8}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")

            elif row['Benefit Type'] == "HOSV":
                local_per_service9 = compare_hosv_with_local(local_data, sob_data)
                if local_per_service9 != sob_int_hosv_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_hosv_value} INSTEAD OF {local_per_service9}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")


            elif row['Benefit Type'] == "SV  ":
                local_per_service10 = compare_sv_with_local(local_data, sob_data)
                if local_per_service10 != sob_int_sv_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_sv_value} INSTEAD OF {local_per_service10}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")
                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")
                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")


            else:
                local_int_chir_value = pd.to_numeric(row['Per Service'], errors='coerce')
                if description == "physiotherapy" and local_int_chir_value != sob_int_chir_value:
                    comments.append(f"INTERNAL LIMIT SHOULD BE {sob_int_chir_value} INSTEAD OF {local_int_chir_value}")

                if local_deductible != sob_deductible_value:
                    comments.append("DEDUCTIBLES SHOULD BE CHANGED")

                if local_family_deductible != sob_familydeductible_value:
                    if not comments:
                        comments.append(f"FAMILY DEDUCTIBLE SHOULD BE {sob_familydeductible_value} INSTEAD OF {local_family_deductible}")

                if pd.to_numeric(local_medicalCOin, errors='coerce') != sob_coinsurance_value:
                    comments.append(f"COINSURANCE PERCENTAGE SHOULD BE {sob_coinsurance_value}% INSTEAD OF {local_medicalCOin}%")

                stoploss_expected_value = round((larger_percentage - smaller_percentage) * threshold)
                if local_stoploss != stoploss_expected_value:
                    comments.append(f"STOPLOSS SHOULD BE {stoploss_expected_value} INSTEAD OF {local_stoploss}")

                if local_major_max != sob_major_max_value:
                    comments.append(f"LTM SHOULD BE {sob_major_max_value} INSTEAD OF {local_major_max}")

            if comments:
                local_data.at[index, 'Comments'] = ', '.join(comments)

    return local_data

def process_data(file_path):
    unhide_columns(file_path, sheet_name='Local')
    xl = pd.ExcelFile(file_path)
    local_data = pd.read_excel(xl, sheet_name='Local')
    sob_data = pd.read_excel(xl, sheet_name='SOB')
    updated_local_data = compare_local_with_sob(local_data, sob_data,user_input)
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        updated_local_data.to_excel(writer, sheet_name='Local', index=False)

if __name__ == "__main__":
    file_path = 'processed/processed_data.xlsx'
    user_input = input("Is this comparison for Active Employees (under 65)? Enter 'yes' or 'no': ").strip().lower()
    
    try:
        process_data(file_path)
        print(f"Processed data saved to the same file: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
