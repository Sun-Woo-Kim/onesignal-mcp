# Complete OneSignal MCP Tools List

The OneSignal MCP server now includes **57 tools** covering all major OneSignal API functionality:

## App Management (5 tools)
1. **list_apps** - List all configured OneSignal apps
2. **add_app** - Add a new OneSignal app configuration locally
3. **update_local_app_config** - Update an existing local app configuration
4. **remove_app** - Remove a local OneSignal app configuration
5. **switch_app** - Switch the current app to use for API requests

## Messaging (8 tools)
6. **send_push_notification** - Send a push notification
7. **send_email** *(NEW)* - Send an email through OneSignal
8. **send_sms** *(NEW)* - Send an SMS/MMS through OneSignal
9. **send_transactional_message** *(NEW)* - Send immediate delivery messages
10. **view_messages** - View recent messages sent
11. **view_message_details** - Get detailed information about a message
12. **view_message_history** - View message history/recipients
13. **cancel_message** - Cancel a scheduled message

## Devices/Players (6 tools)
14. **view_devices** - View devices subscribed to your app
15. **view_device_details** - Get detailed information about a device
16. **add_player** *(NEW)* - Add a new player/device
17. **edit_player** *(NEW)* - Edit an existing player/device
18. **delete_player** *(NEW)* - Delete a player/device record
19. **edit_tags_with_external_user_id** *(NEW)* - Bulk edit tags by external ID

## Segments (3 tools)
20. **view_segments** - List all segments
21. **create_segment** - Create a new segment
22. **delete_segment** - Delete a segment

## Templates (6 tools)
23. **view_templates** - List all templates
24. **view_template_details** - Get template details
25. **create_template** - Create a new template
26. **update_template** *(NEW)* - Update an existing template
27. **delete_template** *(NEW)* - Delete a template
28. **copy_template_to_app** *(NEW)* - Copy template to another app

## Apps (6 tools)
29. **view_app_details** - Get details about configured app
30. **view_apps** - List all organization apps
31. **create_app** - Create a new OneSignal application
32. **update_app** - Update an existing application
33. **view_app_api_keys** - View API keys for an app
34. **create_app_api_key** - Create a new API key

## API Key Management (3 tools) *(NEW)*
35. **delete_app_api_key** - Delete an API key
36. **update_app_api_key** - Update an API key
37. **rotate_app_api_key** - Rotate an API key

## Users (6 tools)
38. **create_user** - Create a new user
39. **view_user** - View user details
40. **update_user** - Update user information
41. **delete_user** - Delete a user
42. **view_user_identity** - Get user identity information
43. **view_user_identity_by_subscription** *(NEW)* - Get identity by subscription

## Aliases (3 tools)
44. **create_or_update_alias** - Create or update user alias
45. **delete_alias** - Delete a user alias
46. **create_alias_by_subscription** *(NEW)* - Create alias by subscription ID

## Subscriptions (5 tools)
47. **create_subscription** - Create a new subscription
48. **update_subscription** - Update a subscription
49. **delete_subscription** - Delete a subscription
50. **transfer_subscription** - Transfer subscription between users
51. **unsubscribe_email** - Unsubscribe using email token

## Live Activities (3 tools) *(NEW)*
52. **start_live_activity** - Start iOS Live Activity
53. **update_live_activity** - Update iOS Live Activity
54. **end_live_activity** - End iOS Live Activity

## Analytics & Export (3 tools) *(NEW)*
55. **view_outcomes** - View outcomes/conversion data
56. **export_players_csv** - Export player data to CSV
57. **export_messages_csv** - Export messages to CSV

## Summary by Category
- **App Management**: 5 tools
- **Messaging**: 8 tools (3 new)
- **Devices/Players**: 6 tools (4 new)
- **Segments**: 3 tools
- **Templates**: 6 tools (3 new)
- **Apps**: 6 tools
- **API Keys**: 3 tools (all new)
- **Users**: 6 tools (1 new)
- **Aliases**: 3 tools (1 new)
- **Subscriptions**: 5 tools
- **Live Activities**: 3 tools (all new)
- **Analytics**: 3 tools (all new)

**Total**: 57 tools (21 newly added) 