import SwiftUI

enum AppPhase {
    case camera
    case analyzing(UIImage)
}

struct ContentView: View {
    @State private var phase: AppPhase = .camera

    var body: some View {
        ZStack {
            Color(hex: 0x1a1814).ignoresSafeArea()

            switch phase {
            case .camera:
                CameraView { image in
                    withAnimation(.easeInOut(duration: 0.3)) {
                        phase = .analyzing(image)
                    }
                }
                .transition(.opacity)

            case .analyzing(let image):
                AnalysisView(image: image) {
                    withAnimation(.easeInOut(duration: 0.3)) {
                        phase = .camera
                    }
                }
                .transition(.opacity)
            }
        }
    }
}
