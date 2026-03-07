import Foundation

enum MockData {
    static let sampleResult = RepairResult(
        repairability: "high",
        difficulty: "easy",
        estimatedTime: "15–25 minutes",
        estimatedCostUsd: 12.99,
        briefDescription: "The office chair caster wheel is cracked and no longer rolls smoothly. This is a very common failure point and replacement wheels are inexpensive and universally sized. No tools beyond a flat-head screwdriver are needed.",
        repairSteps: [
            "Flip the chair upside down or lay it on its side for access.",
            "Grip the damaged caster wheel and pull it straight out of the socket — most casters are friction-fit.",
            "If the caster is stuck, use a flat-head screwdriver to pry it out gently.",
            "Insert the new caster wheel stem into the empty socket and press firmly until it clicks.",
            "Repeat for any other worn wheels, then flip the chair upright and test."
        ],
        partsNeeded: [
            "Replacement office chair caster wheel (standard 11 mm stem)"
        ],
        toolsNeeded: [
            "Flat-head screwdriver"
        ],
        products: RepairResult.Products(
            parts: [
                RepairResult.ProductLink(
                    title: "Office Chair Caster Wheels (Set of 5)",
                    url: "https://www.google.com/search?tbm=shop&q=office+chair+caster+wheels"
                )
            ],
            tools: [
                RepairResult.ProductLink(
                    title: "Stanley 6\" Flat-Head Screwdriver",
                    url: "https://www.google.com/search?tbm=shop&q=flat+head+screwdriver"
                )
            ],
            source: "google_shopping"
        )
    )
}
