# Google Drive CLI Downloader

Google has recently started to enforce stricter limits on file storage, leaving many users scrambling to organize and manage their files before running out of space. While Google Drive is an excellent service for cloud storage, interacting with it can often feel overwhelming when dealing with large amounts of data.

**Introducing Google Drive CLI Downloader** – a simple, lightweight command-line interface (CLI) tool that allows you to quickly and easily interact with your Google Drive. Whether you need to list your files or download them to your local machine, this tool lets you manage your existing files efficiently, without the need to open your browser.

## Features

- **List Files**: View a simple list of all your files stored on Google Drive from the command line.
- **Download Files**: Download your existing Google Drive files to your local `downloads/` folder with just a few commands.
- **Simple Authentication**: Authenticate via your Google account with OAuth 2.0 and manage your files securely.
- **Organize Your Files**: As Google continues to crack down on file storage, use this CLI to download and archive your important files locally.

## Motivation

With Google’s recent changes to storage policies, many users are looking for a way to manage their files more efficiently. Instead of relying solely on Google’s web interface, this CLI provides a more flexible, scriptable solution for power users. Whether you're archiving data, backing up essential files, or managing your cloud storage limits, **Google Drive CLI Downloader** provides a hassle-free experience.

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/KhachDavid/drive-cli.git
    cd drive-cli
    ```

2. **Set Up a Virtual Environment (Optional but Recommended)**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the Required Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Create Google Drive API Credentials**:
   - Head over to the [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the **Google Drive API**.
   - Download the `client_secret.json` file and place it in the root directory of this project.
   - Add your email as a test email to bypass google restrictions

## Usage

1. **Authenticate**:
   The first time you run the script, it will prompt you to authenticate via Google in your browser.
   
    ```bash
    python main.py
    ```

2. **List Your Files**:
   Once authenticated, you can list your Google Drive files:
   
    ```bash
    python main.py --list
    ```

3. **Download Files**:
   To download a file, simply specify the file ID (found using `--list`) and provide a name for the file:
   
    ```bash
    python main.py --download <file_id> <file_name>
    ```

   The file will be downloaded to the `downloads/` directory.

## Example

List your Google Drive files:

```bash
python main.py --list
