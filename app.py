import streamlit as st
import pandas as pd

def main():

    def data_preprocessing(data):
        data = pd.DataFrame(data, columns=['Date', 'Shift', 'Team', 'EPF Number', 'Absenteeism Type', 
            'Status', 'Leave Type', 'Absent/Present', 'Reason', 'DOB', 'Join Date', 'Civil Status', 
            'Gouping Current Month Production Incentive', 'Grouping Current Month Overtime', 
            'Grouping Current Month Net Salary', 'Gouping -1 Month Production Incentive', 
            'Grouping -1 Month Overtime', 'Grouping -1 Month Net Salary', 'Gouping -2 Month Production Incentive', 'Grouping -2 Month Overtime', 'Grouping -2 Month Net Salary', 'Gouping -3 Month Production Incentive', 'Grouping -3 Month Overtime', 'Grouping -3 Month Net Salary'])

        data['Date'] = pd.to_datetime(data['Date'])
        data['DOB'] = pd.to_datetime(data['DOB'])
        data['Join Date'] = pd.to_datetime(data['Join Date'])

        data = data[data['Absent/Present'] != 'MAT']
        data = data[data['Leave Type'] != 0.5]

        # Converted Shift A as 0 and Shift B as 1
        data['Shift'] = data.Shift.map({'Shift A' : 0, 'Shift B' : 1})

        # Filter out teams starting with 'Jumper'
        data = data[~data['Team'].str.startswith('Jump')]
        # Filter out teams starting with 'MAT'
        data = data[~data['Team'].str.startswith('MAT')]
        # Filter out teams starting with 'MT'
        data = data[~data['Team'].str.startswith('MT')]
        # Filter out teams starting with 'MT'
        data = data[~data['Team'].str.startswith('Train')]

        # Define a function to map the labels based on team names
        def label_teams(team_name):
            if team_name.endswith('A'):
                return 0
            elif team_name.endswith('B'):
                return 1
            else:
                return -1  # Default label for other cases, if needed

        # Apply the function to create a new column 'Label'
        data['Teams'] = data['Team'].apply(label_teams)
        data = data.drop(['Team'], axis=1)
        st.write(data)

        # Converted Absenteeism Type attribute, Informed as 0 and Uninformed as 1
        data['Absenteeism Type'] = data['Absenteeism Type'].map({'Informed' : 0, 'Uninformed' : 1})

        # Converted Status attribute, Notified as 0 and Not Notified as 1
        data['Status'] = data.Status.map({'Notified' : 0, 'Not Notified' : 1})

        # Absent Reasons have categorized into three groups
        data['Reason'] = data['Reason'].map({'Personal Reason' : 'Group_2', 'No Message' : 'Group_3',
            'Maternity' : 'Group_2', 'Delayed Swipe' : 'Group_3', 'Health Related' : 'Group_1', 'VOP' : 'Group_3', 'Resignation' : 'Group_2', 'Family Member - Health Related ' : 'Group_1', 'Child Related ' : 'Group_2', 'Medical Leave' : 'Group_1', 'Pregnancy' : 'Group_2', 'Hospitalized' : 'Group_1', 'Funeral ' : 'Group_2', 'Flood' : 'Group_3', 'Natural Disaster ' : 'Group_3', 'Family Member - Other' : 'Group_3', 'Feeding Hour Delay' : 'Group_4', 'Cultural Celebration' : 'Group_3', 'Clinic' : 'Group_1', 'Delayed less 0.5h' : 'Group_4', 'Child Care' : 'Group_2', 'Before Maternity ' : 'Group_2', 'Delayed high 0.5h' : 'Group_4', 'Family Member - Health Related' : 'Group_1', 'Suspended' : 'Group_2', 'After Maternity ' : 'Group_2'})

        data['Reason'] = data.Reason.map({'Group_1' : 0, 'Group_2' : 1, 'Group_3' : 2, 'Group_4' : 3})

        for i in range(1, 7):
            column_name = f'{i}_Weeks_Ago_Absent_Count'
            data[column_name] = data.groupby('EPF Number').apply(
                lambda group: group['Date'].apply(
                    lambda date: group[
                        (group['Date'] >= (date - pd.DateOffset(weeks=i))) & (group['Date'] < (date - pd.DateOffset(weeks=i-1)))
                    ]['EPF Number'].value_counts().get(group['EPF Number'].iat[0], 0)
                )
            ).reset_index(level=0, drop=True)

        # Calculate the summation of value counts for the four weeks before
        data['Sum_6_Weeks_Ago'] = data[[f'{i}_Weeks_Ago_Absent_Count' for i in range(1, 7)]].sum(axis=1)
        st.write(data)

        from datetime import datetime

        # We are calculating employee age using DOB
        now = datetime.now()
        data['Age'] = (now - data['DOB']).astype('<m8[Y]').astype(int)

        # Calculate service time using "Join Date"
        data['Service Time'] = (now - data['Join Date']).astype('<m8[Y]').astype(int)
        data = data.drop(['DOB', 'Join Date'], axis=1)

        data['Age_class'] = pd.cut(data['Age'], bins=[19, 28, 37, 57], labels=[0, 1, 2], include_lowest=True).astype(int)
        data['Service_class'] = pd.cut(data['Service Time'], bins=[0, 3, 13, 29], labels=[0, 1, 2], include_lowest=True).astype(int)

        data = data.drop(['Absent/Present', 'Leave Type', 'Age', 'Service Time'], axis=1)

        data['Civil Status'] = data['Civil Status'].map({'Married' : 0, 'Single' : 1, 'Divorced' : 2, 'Widowed' : 3})

        data = data.drop(data[data['Grouping Current Month Overtime'] == 'Not Indicated'].index)
        data = data.drop(data[data['Gouping Current Month Production Incentive'] == 'Not Indicated'].index)
        data = data.drop(data[data['Grouping Current Month Net Salary'] == 'Not Indicated'].index)
        data = data.drop(data[data['Gouping -1 Month Production Incentive'] == 'Not Indicated'].index)
        data = data.drop(data[data['Grouping -1 Month Overtime'] == 'Not Indicated'].index)
        data = data.drop(data[data['Grouping -1 Month Net Salary'] == 'Not Indicated'].index)
        data = data.drop(data[data['Gouping -2 Month Production Incentive'] == 'Not Indicated'].index)
        data = data.drop(data[data['Grouping -2 Month Net Salary'] == 'Not Indicated'].index)
        data = data.drop(data[data['Grouping -2 Month Overtime'] == 'Not Indicated'].index)
        data = data.drop(data[data['Gouping -3 Month Production Incentive'] == 'Not Indicated'].index)
        data = data.drop(data[data['Grouping -3 Month Overtime'] == 'Not Indicated'].index)
        data = data.drop(data[data['Grouping -3 Month Net Salary'] == 'Not Indicated'].index)

        data['Grouping Current Month Overtime'] = data['Grouping Current Month Overtime'].astype(int)
        data['Gouping Current Month Production Incentive'] = data['Gouping Current Month Production Incentive'].astype(int)
        data['Grouping Current Month Net Salary'] = data['Grouping Current Month Net Salary'].astype(int)
        data['Gouping -1 Month Production Incentive'] = data['Gouping -1 Month Production Incentive'].astype(int)
        data['Grouping -1 Month Overtime'] = data['Grouping -1 Month Overtime'].astype(int)
        data['Grouping -1 Month Net Salary'] = data['Grouping -1 Month Net Salary'].astype(int)
        data['Gouping -2 Month Production Incentive'] = data['Gouping -2 Month Production Incentive'].astype(int)
        data['Grouping -2 Month Net Salary'] = data['Grouping -2 Month Net Salary'].astype(int)
        data['Grouping -2 Month Overtime'] = data['Grouping -2 Month Overtime'].astype(int)
        data['Gouping -3 Month Production Incentive'] = data['Gouping -3 Month Production Incentive'].astype(int)
        data['Grouping -3 Month Overtime'] = data['Grouping -3 Month Overtime'].astype(int)
        data['Grouping -3 Month Net Salary'] = data['Grouping -3 Month Net Salary'].astype(int)

        data['Gouping Current Month Production Incentive'] = data['Gouping Current Month Production Incentive'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Grouping Current Month Overtime'] = data['Grouping Current Month Overtime'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Grouping Current Month Net Salary'] = data['Grouping Current Month Net Salary'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Gouping -1 Month Production Incentive'] = data['Gouping -1 Month Production Incentive'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Grouping -1 Month Overtime'] = data['Grouping -1 Month Overtime'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Grouping -1 Month Net Salary'] = data['Grouping -1 Month Net Salary'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Gouping -2 Month Production Incentive'] = data['Gouping -2 Month Production Incentive'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Grouping -2 Month Overtime'] = data['Grouping -2 Month Overtime'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Grouping -2 Month Net Salary'] = data['Grouping -2 Month Net Salary'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Gouping -3 Month Production Incentive'] = data['Gouping -3 Month Production Incentive'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Grouping -3 Month Overtime'] = data['Grouping -3 Month Overtime'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})
        data['Grouping -3 Month Net Salary'] = data['Grouping -3 Month Net Salary'].map({1 : 1, 2 : 2, 3 : 3, 4 : 4, 5 : 5})

        import datetime
        # Calculate the difference between the 'Date' column and today's date
        data['Date_Difference'] = abs(data['Date'] - datetime.datetime.now())

        st.write("Pre Process Completed")

        return data


    st.set_page_config(page_title="Employee Absenteeism Prediction", page_icon=":smiley:")
    st.title('Employee Absenteeism Prediction')

    uploaded_file = st.file_uploader('Upload an Excel file', type=['xlsx', 'xls'])

    if uploaded_file is not None:
        if uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)

            # # Check for extra columns
            # extra_columns = [col for col in df.columns if col not in ['Date', 'Shift', 'Team', 'EPF Number', 'Absenteeism Type', 'Status', 'Leave Type', 'Absent/Present', 'Reason', 'DOB', 'Join Date', 'Civil Status', 'Gouping Current Month Production Incentive', 'Grouping Current Month Overtime', 'Grouping Current Month Net Salary', 'Gouping -1 Month Production Incentive', 'Grouping -1 Month Overtime', 'Grouping -1 Month Net Salary', 'Gouping -2 Month Production Incentive', 'Grouping -2 Month Overtime', 'Grouping -2 Month Net Salary', 'Gouping -3 Month Production Incentive', 'Grouping -3 Month Overtime', 'Grouping -3 Month Net Salary']]

            # # Check 'Shift' column values
            # invalid_shift_values = df[~df['Shift'].isin(['Shift A', 'Shift B'])]['Shift'].unique()

            # # Check 'Team' column values
            # invalid_team_values = df[~df['Team'].isin(['A', 'B', 'C'])]['Team'].unique()

            # # Check 'Absenteeism Type' column values
            # invalid_absenteeism_type_values = df[~df['Absenteeism Type'].isin(['Informed', 'Uninformed'])]['Absenteeism Type'].unique()

            # # Check 'Status' column values
            # invalid_status_values = df[~df['Status'].isin(['Notified', 'Not Notified'])]['Status'].unique()

            # # Check 'Absent/Present' column values
            # invalid_absent_present_values = df[~df['Absent/Present'].isin(['Absent', 'MAT'])]['Absent/Present'].unique()

            # # Check 'Leave Type' column values
            # invalid_leave_type_values = df[~df['Leave Type'].isin([1, 0])]['Leave Type'].unique()

            # messages = []
            # if extra_columns:
            #     messages.append(f"Please remove additional columns: {', '.join(map(str, extra_columns))}")

            # if invalid_shift_values.any():
            #     messages.append(f"Please remove values other than 'Shift A' and 'Shift B' in 'Shift' column: {', '.join(map(str, invalid_shift_values))}")

            # if invalid_team_values.any():
            #     messages.append(f"Please remove values other than 'A', 'B', 'C' in 'Team' column: {', '.join(map(str, invalid_team_values))}")

            # if messages:
            #     warning_message = "\n\n".join(messages)
            #     st.warning(warning_message)
            # else:
            #     st.write('### Uploaded Excel Data:')
            #     st.write(df)
            #     uploaded_file = None  # Resetting the uploader after successful upload

            data = data_preprocessing(df)

            data_for_all_employees_month = []
            data_for_all_employees_week = []
            data_for_all_employees_day = []

            from datetime import datetime

            current_date = datetime.now()  # Define current_date as the current date
            curr_dat = current_date.strftime('%m/%d/%Y')

            # Load the pre-trained joblib model
            month_model = joblib.load("month.joblib")
            week_model = joblib.load("week.joblib")
            day_model = joblib.load("day_range.joblib")

            st.write("Models Read")

            # Prepare your data for prediction (replace this with your data preprocessing logic)
            columns_to_select = ['Shift', 'Absenteeism Type', 'Status', 'Reason', 'Civil Status', 'Gouping Current Month Production Incentive', 'Grouping Current Month Overtime', 'Grouping Current Month Net Salary', 'Gouping -1 Month Production Incentive', 'Grouping -1 Month Overtime', 'Grouping -1 Month Net Salary', 'Gouping -2 Month Production Incentive', 'Grouping -2 Month Overtime', 'Grouping -2 Month Net Salary', 'Gouping -3 Month Production Incentive', 'Grouping -3 Month Overtime', 'Grouping -3 Month Net Salary', 'Teams', 'Age_class', 'Service_class']

            # Define a mapping between prediction output and months
            month_mapping = {0: 'January', 1: 'February', 2: 'March', 3: 'April', 4: 'May', 5: 'June', 6: 'July', 7: 'August', 8: 'September', 9: 'October', 10: 'November', 11: 'December'}

            # Define a mapping between prediction output and week
            week_mapping = {0: 'Week 1', 1: 'Week 2', 2: 'Week 3', 3: 'Week 4', 4: 'Week 5'}

            # Prepare your data for prediction
            columns_to_week = ['Shift', 'Absenteeism Type', 'Status', 'Reason', 'Civil Status', 'Gouping Current Month Production Incentive', 'Grouping Current Month Overtime', 'Grouping Current Month Net Salary', 'Gouping -1 Month Production Incentive', 'Grouping -1 Month Overtime', 'Grouping -1 Month Net Salary', 'Gouping -2 Month Production Incentive', 'Grouping -2 Month Overtime', 'Grouping -2 Month Net Salary', 'Gouping -3 Month Production Incentive', 'Grouping -3 Month Overtime', 'Grouping -3 Month Net Salary', '1_Weeks_Ago_Absent_Count', '2_Weeks_Ago_Absent_Count', '3_Weeks_Ago_Absent_Count', '4_Weeks_Ago_Absent_Count','5_Weeks_Ago_Absent_Count', '6_Weeks_Ago_Absent_Count', 'Sum_6_Weeks_Ago', 'Teams', 'Age_class', 'Service_class']

            # Define a mapping between prediction output and Day Range
            day_mapping = {0: 'Range 1', 1: 'Range 2', 2: 'Range 3'}

            # Prepare your data for prediction
            columns_to_day_range = ['Shift', 'Absenteeism Type', 'Status', 'Reason', 'Civil Status','Gouping Current Month Production Incentive', 'Grouping Current Month Overtime', 'Grouping Current Month Net Salary', 'Gouping -1 Month Production Incentive', 'Grouping -1 Month Overtime', 'Grouping -1 Month Net Salary', 'Gouping -2 Month Production Incentive', 'Grouping -2 Month Overtime', 'Grouping -2 Month Net Salary', 'Gouping -3 Month Production Incentive', 'Grouping -3 Month Overtime', 'Grouping -3 Month Net Salary', '1_Weeks_Ago_Absent_Count', '2_Weeks_Ago_Absent_Count', '3_Weeks_Ago_Absent_Count', '4_Weeks_Ago_Absent_Count', '5_Weeks_Ago_Absent_Count', '6_Weeks_Ago_Absent_Count', 'Sum_6_Weeks_Ago', 'Teams', 'Age_class', 'Service_class']

            st.write("Data Writing Started")
    
            for epf_number in epfs:
                selected_record = data[data['EPF Number'] == epf_number]

                # Find the row with the nearest date to today
                selected_record = selected_record.loc[selected_record['Date_Difference'].idxmin()]

                # Select the specified columns from the DataFrame
                month = selected_record[columns_to_select]

                # Reshape the input data to be a 2D array
                month = month.values.reshape(1, -1)

                # Make predictions using the loaded model
                probabilities_month = month_model.predict_proba(month)

                # Get the indices of the top twele classes with the highest probabilities
                top_indices_month = probabilities_month.argsort()[0][-12:][::-1]

                # Map the top indices to predicted months
                predicted_months = [month_mapping.get(cls) for cls in top_indices_month]

                # Get the probability values for the top twele classes
                probability_values = probabilities_month[0][top_indices_month]
    
                # Combine and print the values for each record, and break the loop if a probability reaches 0
                for month, prob in zip(predicted_months, probability_values):
                    if prob == 0:
                        break
            
                    # Get the current date
                    today = datetime.today()
        
                    # Convert month name to a month number (1-12)
                    month_number = datetime.strptime(month, '%B').month
        
                    # Get the current year and month
                    current_year = today.year
                    current_month = today.month

                    # Check if the provided month is before the current month
                    if month_number < current_month:
                        # If so, increment the year by 1
                        current_year += 1

                    # Calculate the last day of the provided month
                    last_day = calendar.monthrange(current_year, month_number)[1]

                    # Format the result as 'MM/DD/YYYY'
                    last_day_formatted = f'{month_number}/{last_day}/{current_year}'
        
                    dat_list = [epf_number, last_day_formatted, float(f'{prob:.2f}'), curr_dat]
                    data_for_all_employees_month.append(dat_list)

                    # Select the specified columns from the DataFrame
                    week = selected_record[columns_to_week]
                    week = dict(week)
                    week['Month'] = month_number
        
                    week = pd.DataFrame([week], index=[0])

                    # Use the week_model to predict the week
                    predicted_week_probabilities = week_model.predict_proba(week)

                    # Get the top 5 predicted weeks and their probabilities
                    top_week_indices = predicted_week_probabilities.argsort()[0][-5:][::-1]
        
                    top_week_probabilities = predicted_week_probabilities[0][top_week_indices]

                    # Define a mapping between prediction output and week
                    week_mapping = {0: 'Week 1', 1: 'Week 2', 2: 'Week 3', 3: 'Week 4', 4: 'Week 5'}

                    # Map the top indices to predicted weeks
                    predicted_weeks = [week_mapping.get(cls) for cls in top_week_indices]

                    # Print the top 5 predicted weeks and their probabilities
                    for week, probability, week_num in zip(predicted_weeks, top_week_probabilities, top_week_indices):
                        dat_list_2 = [epf_number, last_day_formatted, week, float(f'{probability:.2f}'), curr_dat]
                        data_for_all_employees_week.append(dat_list_2)
            
                        # Select the specified columns from the DataFrame
                        day = selected_record[columns_to_day_range]
                        day = dict(day)
                        day['Month'] = month_number
                        day['Week Number'] = week_num
            
                        day = pd.DataFrame([day], index=[0])

                        # Use the week_model to predict the week
                        predicted_day_probabilities = day_model.predict_proba(day)

                        # Get the top 5 predicted weeks and their probabilities
                        top_day_indices = predicted_day_probabilities.argsort()[0][-3:][::-1]
                        top_day_probabilities = predicted_day_probabilities[0][top_day_indices]

                        # Define a mapping between prediction output and Day Range
                        day_mapping = {0: 'Range 1', 1: 'Range 2', 2: 'Range 3'}

                        # Map the top indices to predicted weeks
                        predicted_days = [day_mapping.get(cls) for cls in top_day_indices]

                        # Print the top 5 predicted weeks and their probabilities
                        for day, probability in zip(predicted_days, top_day_probabilities):
                            dat_list_3 = [epf_number, last_day_formatted, week, day, float(f'{probability:.2f}'), curr_dat]
                            data_for_all_employees_day.append(dat_list_3)
            
            st.write("Data Writing Completed")

            # Create a DataFrame from the list
            if st.button('Download Excel - Month'):
                # Create a DataFrame from the list
                df_month = pd.DataFrame(data_for_all_employees_month, columns=['EPF Number', 'Absent Month', 'Probability', 'Run Month'])
                # Write the DataFrame to an Excel file, specifying the sheet name
                df_month.to_excel('predicted_data_month.xlsx', sheet_name='Month', index=False, header=True)
                st.download_button(label="Download Excel - Month", data='predicted_data_month.xlsx', file_name='predicted_data_month.xlsx', mime='application/octet-stream')

            if st.button('Download Excel - Week'):
                # Create a DataFrame from the list
                df_week = pd.DataFrame(data_for_all_employees_week, columns=['EPF Number', 'Absent Month', 'Absent Week', 'Probability', 'Run Month'])
                # Write the DataFrame to an Excel file, specifying the sheet name
                df_week.to_excel('predicted_data_week.xlsx', sheet_name='Week', index=False, header=True)
                st.download_button(label="Download Excel - Week", data='predicted_data_week.xlsx', file_name='predicted_data_week.xlsx', mime='application/octet-stream')

            if st.button('Download Excel - Day Range'):
                # Create a DataFrame from the list
                df_day = pd.DataFrame(data_for_all_employees_day, columns=['EPF Number', 'Absent Month', 'Absent Week', 'Absent Day Range', 'Probability', 'Run Month'])
                # Write the DataFrame to an Excel file, specifying the sheet name
                df_day.to_excel('predicted_data_day.xlsx', sheet_name='Day Range', index=False, header=True)
                st.download_button(label="Download Excel - Day Range", data='predicted_data_day.xlsx', file_name='predicted_data_day.xlsx', mime='application/octet-stream')
            
        else:
            st.error('Please upload a valid Excel file (with .xlsx or .xls extension).')

    # Hide the file uploader after successful upload
    if uploaded_file is None:
        uploaded_file = st.empty()  # Replace uploader with an empty slot

if __name__ == "__main__":
    main()
