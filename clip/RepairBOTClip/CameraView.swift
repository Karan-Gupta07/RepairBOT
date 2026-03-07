import SwiftUI
import PhotosUI

struct CameraView: View {
    let onImageSelected: (UIImage) -> Void

    @State private var showPhotoPicker = false
    @State private var showCamera = false

    var body: some View {
        VStack(spacing: 0) {
            Spacer()

            VStack(spacing: 24) {
                Image(systemName: "wrench.and.screwdriver")
                    .font(.system(size: 56))
                    .foregroundColor(Color(hex: 0xd4a03a))

                VStack(spacing: 8) {
                    Text("RepairBOT")
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(Color(hex: 0xf5f0e8))
                    Text("Snap a photo of something broken.\nWe'll tell you how to fix it.")
                        .font(.subheadline)
                        .foregroundColor(Color(hex: 0x8c857c))
                        .multilineTextAlignment(.center)
                }
            }

            Spacer()

            VStack(spacing: 14) {
                Button(action: { showCamera = true }) {
                    Label("Take a Photo", systemImage: "camera.fill")
                        .font(.headline)
                        .frame(maxWidth: .infinity, minHeight: 52)
                        .background(Color(hex: 0xd4a03a))
                        .foregroundColor(Color(hex: 0x1a1814))
                        .cornerRadius(14)
                }

                Button(action: { showPhotoPicker = true }) {
                    Label("Choose from Library", systemImage: "photo.on.rectangle")
                        .font(.headline)
                        .frame(maxWidth: .infinity, minHeight: 52)
                        .background(Color(hex: 0x2e2922))
                        .foregroundColor(Color(hex: 0xf5f0e8))
                        .cornerRadius(14)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14)
                                .stroke(Color(hex: 0x3d3630), lineWidth: 1)
                        )
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 40)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(hex: 0x1a1814))
        .sheet(isPresented: $showPhotoPicker) {
            PhotoPickerView(onImageSelected: onImageSelected)
        }
        .fullScreenCover(isPresented: $showCamera) {
            CameraCaptureView(onImageSelected: onImageSelected)
                .ignoresSafeArea()
        }
    }
}

// MARK: - PHPicker wrapper

struct PhotoPickerView: UIViewControllerRepresentable {
    let onImageSelected: (UIImage) -> Void
    @Environment(\.dismiss) private var dismiss

    func makeUIViewController(context: Context) -> PHPickerViewController {
        var config = PHPickerConfiguration()
        config.filter = .images
        config.selectionLimit = 1
        let picker = PHPickerViewController(configuration: config)
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: PHPickerViewController, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    class Coordinator: NSObject, PHPickerViewControllerDelegate {
        let parent: PhotoPickerView
        init(_ parent: PhotoPickerView) { self.parent = parent }

        func picker(_ picker: PHPickerViewController, didFinishPicking results: [PHPickerResult]) {
            parent.dismiss()
            guard let provider = results.first?.itemProvider,
                  provider.canLoadObject(ofClass: UIImage.self) else { return }
            provider.loadObject(ofClass: UIImage.self) { image, _ in
                if let uiImage = image as? UIImage {
                    DispatchQueue.main.async {
                        self.parent.onImageSelected(uiImage)
                    }
                }
            }
        }
    }
}

// MARK: - UIImagePickerController wrapper for camera

struct CameraCaptureView: UIViewControllerRepresentable {
    let onImageSelected: (UIImage) -> Void
    @Environment(\.dismiss) private var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: CameraCaptureView
        init(_ parent: CameraCaptureView) { self.parent = parent }

        func imagePickerController(_ picker: UIImagePickerController,
                                   didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            parent.dismiss()
            if let image = info[.originalImage] as? UIImage {
                DispatchQueue.main.async {
                    self.parent.onImageSelected(image)
                }
            }
        }

        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }
}

// MARK: - Hex color helper

extension Color {
    init(hex: UInt, opacity: Double = 1.0) {
        self.init(
            .sRGB,
            red: Double((hex >> 16) & 0xFF) / 255,
            green: Double((hex >> 8) & 0xFF) / 255,
            blue: Double(hex & 0xFF) / 255,
            opacity: opacity
        )
    }
}
