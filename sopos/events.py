doc_events = {
	"Item": {
		"on_update": "sopos.soposevents.item.on_update",
		"on_cancel": "sopos.soposevents.item.on_update",
		"on_trash": "sopos.soposevents.item.on_update"
	},
	"Bin": {
		"on_update": "sopos.soposevents.data.on_update",
		"on_cancel": "sopos.soposevents.data.on_update",
		"on_trash": "sopos.soposevents.data.on_update"
	},
	"Pricing Rule": {
		"on_update": "sopos.soposevents.pricing_rule.on_update",
		"on_cancel": "sopos.soposevents.pricing_rule.on_update",
		"on_trash": "sopos.soposevents.pricing_rule.on_update"
	}
}
