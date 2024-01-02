# ZyShift, an Automated Shift Scheduling / Reminding Internal Tool for the ZyBooks Support Team

## Project Description
This project is designed to automate the process of synchronizing work hours (accross all US time zones) from a Google Sheets document to Google Calendar and providing timely reminders before shifts. Utilizing the Google Cloud Platform (GCP) services, it comprises two primary components:

### 1. Schedule Synchronization
- **Functionality**: A script or application will read work hour entries from a Google Sheets document and subsequently create or update events in the user's Google Calendar to reflect the work schedule accurately.

### 2. Reminder Notifications
- **Functionality**: Implements a Google Cloud Function to send reminders to the user 15 minutes before each shift starts, ensuring timely alerts and efficient schedule management.

## Key Features
- **API Integration**: Uses Google Sheets and Calendar APIs for seamless data retrieval and calendar synchronization.
- **Automation**: Leverages Google Cloud Scheduler for the automated execution of the synchronization script.
- **Timely Reminders**: Manages reminder delivery using Google Cloud Functions.
- **User Convenience**: Offers a streamlined solution for managing work schedules, enhancing user productivity.

## Technologies Used
- **Google Cloud Platform (GCP)**: Utilizes various GCP services, including App Engine, Cloud Functions, Cloud Scheduler, Google Cloud Storage, and Pub/Sub
- **Programming Language**: Python for backend development.
- **Google APIs**: Integration with Google Sheets and Calendar for data handling.
- **Pandas (Python Package)**: Interaction with Spreadsheet Cells and Reading their Values.
- **Regular Expression (Python Library)**: Filtered Agent Names to Properly Set Shift Times.
- **Datetime (Python Library)**: Streamlined RFC3339 Formatting Process for Calendar API Use.

## Outcome
The completion of this project will result in an efficient, cloud-based system that effectively integrates Google Sheets with Google Calendar. It showcases the practical application of cloud computing services in automating and simplifying routine productivity tasks.

## Example

**Sample Google Sheets Schedule (Week 01/01/2024 - 01/07/2024):**

![sample google sheets schedule image](https://github.com/kodarfour/GCloudSync-WorkScheduler/blob/kofi-testing/images/example_schedule.png?raw=true)

**Calendar Result (Agent: Kofi | Time Zone: Eastern):**

![calendar result image](https://github.com/kodarfour/GCloudSync-WorkScheduler/blob/kofi-testing/images/result.jpg?raw=true)