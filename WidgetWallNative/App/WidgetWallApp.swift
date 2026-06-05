import SwiftUI

struct WidgetWallMenuContent: View {
    var body: some View {
        Button("Widgets are installed!") { }
            .disabled(true)
        Divider()
        Button("Quit") {
            NSApplication.shared.terminate(nil)
        }
        .keyboardShortcut("q")
    }
}

struct WidgetWallSettingsView: View {
    var body: some View {
        Text("Settings go here")
            .frame(width: 240, height: 120)
            .padding()
    }
}

@main
struct WidgetWallApp: App {
    var body: some Scene {
        MenuBarExtra("WidgetWall", systemImage: "rectangle.3.group") {
            WidgetWallMenuContent()
        }
        Settings {
            WidgetWallSettingsView()
        }
    }
}
#Preview {
    WidgetWallApp()
}

