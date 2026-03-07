import Foundation

struct RepairResult: Codable, Identifiable {
    let id = UUID()
    let repairability: String
    let difficulty: String
    let estimatedTime: String
    let estimatedCostUsd: Double?
    let briefDescription: String
    let repairSteps: [String]
    let partsNeeded: [String]
    let toolsNeeded: [String]
    let products: Products

    struct Products: Codable {
        let parts: [ProductLink]
        let tools: [ProductLink]
        let source: String
    }

    struct ProductLink: Codable, Identifiable {
        let id = UUID()
        let title: String
        let url: String

        enum CodingKeys: String, CodingKey {
            case title, url
        }
    }

    enum CodingKeys: String, CodingKey {
        case repairability, difficulty, products
        case estimatedTime = "estimated_time"
        case estimatedCostUsd = "estimated_cost_usd"
        case briefDescription = "brief_description"
        case repairSteps = "repair_steps"
        case partsNeeded = "parts_needed"
        case toolsNeeded = "tools_needed"
    }
}
