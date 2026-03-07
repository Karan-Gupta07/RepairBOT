import SwiftUI

struct AnalysisView: View {
    let image: UIImage
    let onReset: () -> Void

    @State private var result: RepairResult?
    @State private var isLoading = true
    @State private var isDemoMode = false

    var body: some View {
        ScrollView {
            VStack(spacing: 0) {
                if isLoading {
                    loadingContent
                } else if let result = result {
                    resultsContent(result)
                }
            }
        }
        .background(Color(hex: 0x1a1814))
        .task { await fetchAnalysis() }
    }

    // MARK: - Loading

    private var loadingContent: some View {
        VStack(spacing: 24) {
            Spacer().frame(height: 80)

            Image(uiImage: image)
                .resizable()
                .scaledToFit()
                .frame(maxHeight: 220)
                .cornerRadius(16)
                .shadow(color: .black.opacity(0.4), radius: 12, y: 6)

            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: Color(hex: 0xd4a03a)))
                .scaleEffect(1.3)

            Text("Analyzing your item…")
                .font(.headline)
                .foregroundColor(Color(hex: 0xb8b0a4))

            Spacer()
        }
        .frame(maxWidth: .infinity)
        .padding(.horizontal, 24)
    }

    // MARK: - Results

    private func resultsContent(_ result: RepairResult) -> some View {
        VStack(spacing: 20) {
            if isDemoMode {
                demoBanner
            }

            Image(uiImage: image)
                .resizable()
                .scaledToFit()
                .frame(maxHeight: 180)
                .cornerRadius(14)
                .shadow(color: .black.opacity(0.3), radius: 8, y: 4)
                .padding(.top, 16)

            repairabilityBadge(result)

            infoCards(result)

            descriptionSection(result)

            stepsSection(result)

            if !result.partsNeeded.isEmpty || !result.toolsNeeded.isEmpty {
                needsSection(result)
            }

            if !result.products.parts.isEmpty || !result.products.tools.isEmpty {
                productsSection(result)
            }

            Button(action: onReset) {
                Label("Analyze Another Item", systemImage: "arrow.counterclockwise")
                    .font(.headline)
                    .frame(maxWidth: .infinity, minHeight: 52)
                    .background(Color(hex: 0xd4a03a))
                    .foregroundColor(Color(hex: 0x1a1814))
                    .cornerRadius(14)
            }
            .padding(.top, 8)
            .padding(.bottom, 40)
        }
        .padding(.horizontal, 20)
    }

    // MARK: - Components

    private var demoBanner: some View {
        HStack(spacing: 8) {
            Image(systemName: "info.circle.fill")
            Text("Demo mode — API unavailable")
                .font(.subheadline.weight(.medium))
        }
        .foregroundColor(Color(hex: 0x1a1814))
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .frame(maxWidth: .infinity)
        .background(Color(hex: 0xfacc15))
        .cornerRadius(10)
    }

    private func repairabilityBadge(_ result: RepairResult) -> some View {
        VStack(spacing: 6) {
            Text("Repairability")
                .font(.caption)
                .foregroundColor(Color(hex: 0x8c857c))
                .textCase(.uppercase)
                .tracking(1)

            Text(result.repairability.capitalized)
                .font(.system(size: 28, weight: .bold))
                .foregroundColor(repairabilityColor(result.repairability))

            HStack(spacing: 16) {
                tagPill(icon: "gauge.medium", text: result.difficulty.capitalized)
                if let cost = result.estimatedCostUsd {
                    tagPill(icon: "dollarsign.circle", text: String(format: "$%.2f", cost))
                }
                tagPill(icon: "clock", text: result.estimatedTime)
            }
            .padding(.top, 4)
        }
        .padding(20)
        .frame(maxWidth: .infinity)
        .background(Color(hex: 0x242019))
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(repairabilityColor(result.repairability).opacity(0.4), lineWidth: 1)
        )
    }

    private func tagPill(icon: String, text: String) -> some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .font(.caption2)
            Text(text)
                .font(.caption)
        }
        .foregroundColor(Color(hex: 0xb8b0a4))
    }

    private func infoCards(_ result: RepairResult) -> some View {
        HStack(spacing: 12) {
            infoCard(title: "Difficulty", value: result.difficulty.capitalized,
                     icon: "gauge.medium", color: difficultyColor(result.difficulty))
            infoCard(title: "Est. Cost",
                     value: result.estimatedCostUsd.map { String(format: "$%.0f", $0) } ?? "N/A",
                     icon: "dollarsign.circle", color: Color(hex: 0xd4a03a))
            infoCard(title: "Time", value: result.estimatedTime,
                     icon: "clock", color: Color(hex: 0xb8b0a4))
        }
    }

    private func infoCard(title: String, value: String, icon: String, color: Color) -> some View {
        VStack(spacing: 6) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(color)
            Text(value)
                .font(.subheadline.weight(.semibold))
                .foregroundColor(Color(hex: 0xf5f0e8))
                .multilineTextAlignment(.center)
                .lineLimit(2)
                .minimumScaleFactor(0.75)
            Text(title)
                .font(.caption2)
                .foregroundColor(Color(hex: 0x8c857c))
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 14)
        .background(Color(hex: 0x242019))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(Color(hex: 0x3d3630), lineWidth: 1)
        )
    }

    private func descriptionSection(_ result: RepairResult) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionHeader("Assessment")
            Text(result.briefDescription)
                .font(.subheadline)
                .foregroundColor(Color(hex: 0xb8b0a4))
                .fixedSize(horizontal: false, vertical: true)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color(hex: 0x242019))
        .cornerRadius(14)
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color(hex: 0x3d3630), lineWidth: 1)
        )
    }

    private func stepsSection(_ result: RepairResult) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            sectionHeader("Repair Steps")
            ForEach(Array(result.repairSteps.enumerated()), id: \.offset) { index, step in
                HStack(alignment: .top, spacing: 12) {
                    Text("\(index + 1)")
                        .font(.caption.weight(.bold))
                        .foregroundColor(Color(hex: 0x1a1814))
                        .frame(width: 24, height: 24)
                        .background(Color(hex: 0xd4a03a))
                        .clipShape(Circle())

                    Text(step)
                        .font(.subheadline)
                        .foregroundColor(Color(hex: 0xb8b0a4))
                        .fixedSize(horizontal: false, vertical: true)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color(hex: 0x242019))
        .cornerRadius(14)
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color(hex: 0x3d3630), lineWidth: 1)
        )
    }

    private func needsSection(_ result: RepairResult) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            if !result.partsNeeded.isEmpty {
                sectionHeader("Parts Needed")
                ForEach(result.partsNeeded, id: \.self) { part in
                    bulletItem(part)
                }
            }
            if !result.toolsNeeded.isEmpty {
                sectionHeader("Tools Needed")
                ForEach(result.toolsNeeded, id: \.self) { tool in
                    bulletItem(tool)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color(hex: 0x242019))
        .cornerRadius(14)
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color(hex: 0x3d3630), lineWidth: 1)
        )
    }

    private func productsSection(_ result: RepairResult) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            sectionHeader("Shop")
            HStack(spacing: 4) {
                Image(systemName: "cart")
                    .font(.caption2)
                Text("via \(result.products.source.replacingOccurrences(of: "_", with: " ").capitalized)")
                    .font(.caption)
            }
            .foregroundColor(Color(hex: 0x8c857c))

            ForEach(result.products.parts) { link in
                productRow(link, icon: "gearshape")
            }
            ForEach(result.products.tools) { link in
                productRow(link, icon: "wrench")
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color(hex: 0x242019))
        .cornerRadius(14)
        .overlay(
            RoundedRectangle(cornerRadius: 14)
                .stroke(Color(hex: 0x3d3630), lineWidth: 1)
        )
    }

    private func productRow(_ link: RepairResult.ProductLink, icon: String) -> some View {
        Link(destination: URL(string: link.url) ?? URL(string: "https://google.com")!) {
            HStack(spacing: 10) {
                Image(systemName: icon)
                    .foregroundColor(Color(hex: 0xd4a03a))
                Text(link.title)
                    .font(.subheadline)
                    .foregroundColor(Color(hex: 0xf5f0e8))
                Spacer()
                Image(systemName: "arrow.up.right.square")
                    .font(.caption)
                    .foregroundColor(Color(hex: 0x8c857c))
            }
            .padding(12)
            .background(Color(hex: 0x2e2922))
            .cornerRadius(10)
        }
    }

    // MARK: - Helpers

    private func sectionHeader(_ title: String) -> some View {
        Text(title)
            .font(.headline)
            .foregroundColor(Color(hex: 0xf5f0e8))
    }

    private func bulletItem(_ text: String) -> some View {
        HStack(alignment: .top, spacing: 8) {
            Circle()
                .fill(Color(hex: 0xd4a03a))
                .frame(width: 6, height: 6)
                .padding(.top, 6)
            Text(text)
                .font(.subheadline)
                .foregroundColor(Color(hex: 0xb8b0a4))
        }
    }

    private func repairabilityColor(_ level: String) -> Color {
        switch level.lowercased() {
        case "high": return Color(hex: 0x4ade80)
        case "medium": return Color(hex: 0xfacc15)
        case "low": return Color(hex: 0xf87171)
        default: return Color(hex: 0xb8b0a4)
        }
    }

    private func difficultyColor(_ level: String) -> Color {
        switch level.lowercased() {
        case "easy": return Color(hex: 0x4ade80)
        case "moderate": return Color(hex: 0xfacc15)
        case "hard": return Color(hex: 0xf87171)
        default: return Color(hex: 0xb8b0a4)
        }
    }

    // MARK: - Network

    private func fetchAnalysis() async {
        isLoading = true
        do {
            let apiResult = try await APIService.analyze(image: image)
            result = apiResult
            isDemoMode = false
        } catch {
            result = MockData.sampleResult
            isDemoMode = true
        }
        isLoading = false
    }
}
