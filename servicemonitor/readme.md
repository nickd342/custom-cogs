# Service Monitor

A simple Discord Redbot (V3) cog that helps you monitor your services and websites. Whether you're running a home server, managing multiple websites, or just want to keep an eye on your favorite services, this cog will display the status of multiple services using an embedded discord message.

## Features

This cog monitors your specified services at a set interval and provides status updates in your designated Discord channel. Each status update includes:

- A timestamp of when the check was performed
- Clear visual indicators: 🟢 for online services and 🔴 for offline ones
- A comprehensive list of all monitored services in one message

## Installation

To add this cog to your Discord Redbot, follow these steps:

Pre-requisite: the downloader cog must be loaded and you must have predefined your storage/install paths

1. Add the repository to your bot:

```bash
[p]repo add custom-cogs https://github.com/nickd342/custom-cogs
```

2. Install the cog:

```bash
[p]cog install custom-cogs servicemonitor
```

3. Load the cog:

```bash
[p]load servicemonitor
```

## Setting Up Your First Monitor

Here's a complete example of setting up monitoring for an Emby server:

1. First, create a dedicated channel in your Discord server for status updates.

2. Enable Developer Mode in Discord:

   - Open User Settings
   - Go to App Settings → Advanced
   - Turn on Developer Mode

3. Get your channel's ID:

   - Right-click the channel you created
   - Click "Copy ID" at the bottom of the menu

4. Configure the monitor:

```bash
# Set the channel for status updates
[p]monitor channel 123456789

# Set how often to check (300 seconds = 5 minutes)
[p]monitor interval 300

# Add your first service
[p]monitor add emby https://myembyserver.com
```

## Command Reference

Here's everything you can do with the Service Monitor:

`[p]monitor channel <channel_id>`
Set where status updates should be posted. The channel ID must be a valid Discord channel ID where your bot has permission to send messages.

`[p]monitor interval <seconds>`
Set how often services should be checked. The minimum is 60 seconds to prevent excessive API requests. We recommend 300 seconds (5 minutes) for most use cases.

`[p]monitor add <name> <url>`
Add a new service to your monitoring list. The name should be a simple identifier for the service, and the URL should be the complete URL including http:// or https://.

`[p]monitor remove <name>`
Remove a service from monitoring. Use the same name you used when adding the service.

`[p]monitor list`
View all currently monitored services and their URLs. Useful for checking your current configuration.

## Troubleshooting

If you're not seeing status updates:

1. Verify the bot has permission to send messages in your chosen channel
2. Check that you've set a valid channel ID
3. Ensure at least one service is added to the monitoring list
4. Confirm your check interval is set appropriately
5. Complete the pre-requisites
6. As a last resort, uninstall/remove the cog and then reinstall it.

## Support

If you encounter any issues or have suggestions for improvements, please open an issue on the GitHub repository.

## Contributing

Contributions are welcome! Feel free to submit pull requests or open issues for any bugs you find or features you'd like to see added.

## License

This project is licensed under the GNU General Public License - see the LICENSE file for details.
