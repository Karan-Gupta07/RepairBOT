import Foundation
import UIKit

enum APIError: LocalizedError {
    case invalidImage
    case invalidURL
    case serverError(Int)
    case decodingFailed(Error)

    var errorDescription: String? {
        switch self {
        case .invalidImage:
            return "Could not convert the image to JPEG data."
        case .invalidURL:
            return "The API URL is invalid."
        case .serverError(let code):
            return "Server returned status \(code)."
        case .decodingFailed(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        }
    }
}

enum APIService {
    // Change this to your deployed server URL in production
    static var baseURL = "http://localhost:8000"

    static func analyze(image: UIImage) async throws -> RepairResult {
        guard let jpegData = image.jpegData(compressionQuality: 0.85) else {
            throw APIError.invalidImage
        }

        guard let url = URL(string: "\(baseURL)/analyze") else {
            throw APIError.invalidURL
        }

        let boundary = UUID().uuidString
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 60

        var body = Data()
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"image\"; filename=\"photo.jpg\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
        body.append(jpegData)
        body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body

        let (data, response) = try await URLSession.shared.data(for: request)

        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode != 200 {
            throw APIError.serverError(httpResponse.statusCode)
        }

        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        do {
            return try decoder.decode(RepairResult.self, from: data)
        } catch {
            throw APIError.decodingFailed(error)
        }
    }
}
