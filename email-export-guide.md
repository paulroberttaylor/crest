# Email Export Guide

## Domains to Include

When exporting emails, please provide the domains for:
- Crest Nicholson (e.g., @crestnicholson.com)
- NHOS (New Homes Ombudsman Service)
- Your solicitors' firm

## Export Instructions by Email Client

### Gmail
1. Go to [Google Takeout](https://takeout.google.com/)
2. Deselect all products except "Mail"
3. Click "All Mail data included" and choose "Select labels"
4. Use Gmail search to create a label for relevant emails:
   - Search: `from:(@domain1.com OR @domain2.com) OR to:(@domain1.com OR @domain2.com)`
5. Export in MBOX format

### Outlook Desktop
1. File → Open & Export → Import/Export
2. Choose "Export to a file"
3. Select "Outlook Data File (.pst)"
4. Use Search Folders to filter by domains
5. Convert PST to MBOX using a tool like [PST Converter](https://github.com/epfromer/pst2mbox)

### Apple Mail
1. Select relevant mailbox or create Smart Mailbox with domain filters
2. Mailbox → Export Mailbox
3. Saves as MBOX format directly

### Thunderbird
1. Install ImportExportTools NG addon
2. Right-click on folder → ImportExportTools NG → Export folder
3. Choose MBOX format

## Search Queries

Once you provide the specific domains, I can create exact search queries for filtering the relevant emails.