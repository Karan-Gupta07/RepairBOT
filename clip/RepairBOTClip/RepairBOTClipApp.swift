import SwiftUI

@main
struct RepairBOTClipApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { activity in
                    handleIncomingURL(activity.webpageURL)
                }
        }
    }

    private func handleIncomingURL(_ url: URL?) {
        guard let url = url,
              let host = url.host,
              host.contains("repairbot.app"),
              url.path.hasPrefix("/repair") else { return }
        // The app opens to ContentView which starts in .camera phase,
        // so no additional navigation is needed for the base invocation URL.
    }
}
