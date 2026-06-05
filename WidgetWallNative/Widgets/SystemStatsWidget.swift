import SwiftUI
import WidgetKit

struct SystemStatsProvider: TimelineProvider {
    func placeholder(in context: Context) -> SystemStatsEntry {
        SystemStatsEntry(date: Date(), cpu: 45.2, mem: 62.1)
    }

    func getSnapshot(in context: Context, completion: @escaping (SystemStatsEntry) -> Void) {
        let entry = SystemStatsEntry(date: Date(), cpu: 45.2, mem: 62.1)
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<SystemStatsEntry>) -> Void) {
        // In a real app, you would read actual stats here using ProcessInfo or a shared UserDefaults container
        let entry = SystemStatsEntry(date: Date(), cpu: Double.random(in: 10...90), mem: Double.random(in: 40...80))
        
        // Update every 15 minutes (WidgetKit limit for automatic updates)
        let nextUpdate = Calendar.current.date(byAdding: .minute, value: 15, to: Date())!
        let timeline = Timeline(entries: [entry], policy: .after(nextUpdate))
        completion(timeline)
    }
}

struct SystemStatsEntry: TimelineEntry {
    let date: Date
    let cpu: Double
    let mem: Double
}

struct SystemStatsWidgetEntryView: View {
    var entry: SystemStatsProvider.Entry
    
    var themeColor: Color {
        if entry.cpu > 80 {
            return Color(red: 1.0, green: 0.1, blue: 0.2)
        } else if entry.cpu > 50 {
            return Color(red: 1.0, green: 0.7, blue: 0.0)
        } else {
            return Color(red: 0.0, green: 1.0, blue: 0.8)
        }
    }
    
    var targetText: String {
        if entry.cpu > 80 {
            return "[ CRITICAL: HIGH LOAD ]"
        } else if entry.cpu > 50 {
            return "[ SCANNING ANOMALIES ]"
        } else {
            return "[ TARGET LOCKED ]"
        }
    }

    var body: some View {
        ZStack {
            // Glassmorphic / Dark Background
            Color.black.opacity(0.8)
            
            // Grid Lines
            GridLines()
                .stroke(Color.white.opacity(0.04), lineWidth: 1)
            
            // Target Brackets
            TargetBrackets()
                .stroke(themeColor, lineWidth: 3)
                .shadow(color: themeColor, radius: 5)
                .padding(15)
            
            // Crosshair
            Crosshair()
                .stroke(Color.white.opacity(0.2), lineWidth: 1.5)
                .frame(width: 40, height: 40)
            
            VStack {
                HStack {
                    Text(String(format: "CPU: %04.1f%%", entry.cpu))
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(themeColor)
                        .shadow(color: themeColor, radius: 4)
                    
                    Spacer()
                    
                    Text(String(format: "MEM: %04.1f%%", entry.mem))
                        .font(.system(size: 14, weight: .bold, design: .monospaced))
                        .foregroundColor(themeColor)
                        .shadow(color: themeColor, radius: 4)
                }
                .padding(.top, 30)
                .padding(.horizontal, 25)
                
                Spacer()
                
                Text(targetText)
                    .font(.system(size: 10, weight: .bold, design: .monospaced))
                    .foregroundColor(themeColor)
                    .shadow(color: themeColor, radius: 4)
                
                Spacer()
                
                HStack {
                    Text("SYS.REKO.V1")
                        .font(.system(size: 8, weight: .bold, design: .monospaced))
                        .foregroundColor(Color.white.opacity(0.6))
                    
                    Spacer()
                    
                    Text("USR: XPLICTLY")
                        .font(.system(size: 8, weight: .bold, design: .monospaced))
                        .foregroundColor(Color.white.opacity(0.6))
                }
                .padding(.bottom, 25)
                .padding(.horizontal, 25)
            }
        }
    }
}

struct GridLines: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        let step: CGFloat = 30
        for x in stride(from: 0, to: rect.width, by: step) {
            path.move(to: CGPoint(x: x, y: 0))
            path.addLine(to: CGPoint(x: x, y: rect.height))
        }
        for y in stride(from: 0, to: rect.height, by: step) {
            path.move(to: CGPoint(x: 0, y: y))
            path.addLine(to: CGPoint(x: rect.width, y: y))
        }
        return path
    }
}

struct TargetBrackets: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        let length: CGFloat = 30
        
        // Top Left
        path.move(to: CGPoint(x: rect.minX, y: rect.minY + length))
        path.addLine(to: CGPoint(x: rect.minX, y: rect.minY))
        path.addLine(to: CGPoint(x: rect.minX + length, y: rect.minY))
        
        // Top Right
        path.move(to: CGPoint(x: rect.maxX - length, y: rect.minY))
        path.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
        path.addLine(to: CGPoint(x: rect.maxX, y: rect.minY + length))
        
        // Bottom Right
        path.move(to: CGPoint(x: rect.maxX, y: rect.maxY - length))
        path.addLine(to: CGPoint(x: rect.maxX, y: rect.maxY))
        path.addLine(to: CGPoint(x: rect.maxX - length, y: rect.maxY))
        
        // Bottom Left
        path.move(to: CGPoint(x: rect.minX + length, y: rect.maxY))
        path.addLine(to: CGPoint(x: rect.minX, y: rect.maxY))
        path.addLine(to: CGPoint(x: rect.minX, y: rect.maxY - length))
        
        return path
    }
}

struct Crosshair: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        let cx = rect.midX
        let cy = rect.midY
        let size = rect.width / 2
        
        path.move(to: CGPoint(x: cx - size, y: cy))
        path.addLine(to: CGPoint(x: cx + size, y: cy))
        path.move(to: CGPoint(x: cx, y: cy - size))
        path.addLine(to: CGPoint(x: cx, y: cy + size))
        
        path.addArc(center: CGPoint(x: cx, y: cy), radius: 4, startAngle: .zero, endAngle: .degrees(360), clockwise: true)
        
        return path
    }
}

struct SystemStatsWidget: Widget {
    let kind: String = "SystemStatsWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: SystemStatsProvider()) { entry in
            SystemStatsWidgetEntryView(entry: entry)
                .containerBackground(.black.opacity(0.8), for: .widget)
        }
        .configurationDisplayName("System Stats Target Lock")
        .description("Keep an eye on system resources with a tactical HUD.")
        .supportedFamilies([.systemMedium, .systemLarge])
    }
}
