import tickets.templates as templates

options = [
	# {
	# 	"emoji": "💳",
	# 	"title": "Contact Management",
	# 	"ticket_name": "manage",
	# 	"description": "What do you need help with?"
	# },
	# {
	# 	"emoji": "🍆",
	# 	"title": "Whitelist Application",
	# 	"description": "Please copy & paste the template for each part once all guidelines are met.\n\nObtain your hex from: <http://vacbanned.com/>.",
	# 	"ticket_name": "whitelist",
	# 	"fields": [
	# 		{
	# 			"name": "Guidelines",
	# 			"value": templates.whitelist_guidelines
	# 		},
	# 		{
	# 			"name": "Questions (Part 1)",
	# 			"value": templates.whitelist_template_1
	# 		},
	# 		{
	# 			"name": "Scenarios (Part 2)",
	# 			"value": templates.whitelist_template_2
	# 		},
	# 		{
	# 			"name": "Information (Part 3)",
	# 			"value": templates.whitelist_template_3
	# 		}
	# 	]
	# },
	{
		"emoji": "🔨",
		"title": "Player Report",
		"ticket_name": "report",
		"category": "Reports",
		"fields": [
			{
				"name": "Guidelines",
				"value": templates.player_report_guidelines
			},
			{
				"name": "Template",
				"value": templates.player_report
			}
		]
	},
	{
		"emoji": "🤑",
		"title": "Refund",
		"ticket_name": "refund",
		"fields": [
			{
				"name": "Guidelines",
				"value": templates.refund_report_guidelines
			},
			{
				"name": "Template",
				"value": templates.refund_report
			},
		]
	},
	{
		"emoji": "🤷",
		"title": "Issue",
		"ticket_name": "issue",
		"description": "What problem are you having?\n\nPlease keep in mind that tickets are not meant for bug reports (https://nonstoprp.net/index.php?forums/bug-reports.137/)."
	},
	{
		"emoji": "📣",
		"title": "Other",
		"description": "The Support Team will be with you shortly... Meanwhile, explain what you need help with."
	},
]