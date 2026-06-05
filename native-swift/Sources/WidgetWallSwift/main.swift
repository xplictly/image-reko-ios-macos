import Cocoa
import QuartzCore

class ViewfinderHUDView: NSView {
    var themeColor: NSColor = NSColor(calibratedRed: 0.0, green: 1.0, blue: 0.8, alpha: 1.0)
    
    // Layers
    var bracketsLayer = CAShapeLayer()
    var gridLayer = CAShapeLayer()
    var crosshairLayer = CAShapeLayer()
    
    // Labels
    var cpuLabel = NSTextField()
    var memLabel = NSTextField()
    var brandLabel1 = NSTextField()
    var brandLabel2 = NSTextField()
    var targetLockLabel = NSTextField()
    
    var cpu: Double = 0 {
        didSet { updateStats() }
    }
    
    var mem: Double = 0 {
        didSet { updateStats() }
    }
    
    override init(frame: NSRect) {
        super.init(frame: frame)
        self.wantsLayer = true
        self.layer?.masksToBounds = true
        
        setupGrid()
        setupBrackets()
        setupCrosshair()
        setupLabels()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    func setupGrid() {
        let path = CGMutablePath()
        let step: CGFloat = 30
        for x in stride(from: 0, to: frame.width, by: step) {
            path.move(to: CGPoint(x: x, y: 0))
            path.addLine(to: CGPoint(x: x, y: frame.height))
        }
        for y in stride(from: 0, to: frame.height, by: step) {
            path.move(to: CGPoint(x: 0, y: y))
            path.addLine(to: CGPoint(x: frame.width, y: y))
        }
        gridLayer.path = path
        gridLayer.strokeColor = NSColor.white.withAlphaComponent(0.04).cgColor
        gridLayer.lineWidth = 1
        self.layer?.addSublayer(gridLayer)
    }
    
    func setupBrackets() {
        let path = CGMutablePath()
        let length: CGFloat = 40
        let w = frame.width
        let h = frame.height
        let inset: CGFloat = 20
        
        // Top Left
        path.move(to: CGPoint(x: inset, y: h - inset - length))
        path.addLine(to: CGPoint(x: inset, y: h - inset))
        path.addLine(to: CGPoint(x: inset + length, y: h - inset))
        
        // Top Right
        path.move(to: CGPoint(x: w - inset - length, y: h - inset))
        path.addLine(to: CGPoint(x: w - inset, y: h - inset))
        path.addLine(to: CGPoint(x: w - inset, y: h - inset - length))
        
        // Bottom Right
        path.move(to: CGPoint(x: w - inset, y: inset + length))
        path.addLine(to: CGPoint(x: w - inset, y: inset))
        path.addLine(to: CGPoint(x: w - inset - length, y: inset))
        
        // Bottom Left
        path.move(to: CGPoint(x: inset + length, y: inset))
        path.addLine(to: CGPoint(x: inset, y: inset))
        path.addLine(to: CGPoint(x: inset, y: inset + length))
        
        bracketsLayer.path = path
        bracketsLayer.strokeColor = themeColor.cgColor
        bracketsLayer.fillColor = NSColor.clear.cgColor
        bracketsLayer.lineWidth = 3
        bracketsLayer.shadowColor = themeColor.cgColor
        bracketsLayer.shadowRadius = 10
        bracketsLayer.shadowOpacity = 0.9
        bracketsLayer.shadowOffset = .zero
        self.layer?.addSublayer(bracketsLayer)
    }
    
    func setupCrosshair() {
        let path = CGMutablePath()
        let cx = frame.width / 2
        let cy = frame.height / 2
        let size: CGFloat = 20
        
        path.move(to: CGPoint(x: cx - size, y: cy))
        path.addLine(to: CGPoint(x: cx + size, y: cy))
        path.move(to: CGPoint(x: cx, y: cy - size))
        path.addLine(to: CGPoint(x: cx, y: cy + size))
        
        // Center circle
        path.addArc(center: CGPoint(x: cx, y: cy), radius: 6, startAngle: 0, endAngle: .pi * 2, clockwise: true)
        
        crosshairLayer.path = path
        crosshairLayer.strokeColor = NSColor.white.withAlphaComponent(0.2).cgColor
        crosshairLayer.fillColor = NSColor.clear.cgColor
        crosshairLayer.lineWidth = 1.5
        self.layer?.addSublayer(crosshairLayer)
    }
    
    func createLabel(text: String, size: CGFloat, color: NSColor, x: CGFloat, y: CGFloat, width: CGFloat, alignment: NSTextAlignment = .left) -> NSTextField {
        let lbl = NSTextField(labelWithString: text)
        lbl.font = NSFont(name: "Menlo-Bold", size: size) ?? NSFont.monospacedSystemFont(ofSize: size, weight: .bold)
        lbl.textColor = color
        lbl.alignment = alignment
        lbl.isEditable = false
        lbl.isSelectable = false
        lbl.isBezeled = false
        lbl.drawsBackground = false
        lbl.frame = NSRect(x: x, y: y, width: width, height: size + 10)
        self.addSubview(lbl)
        return lbl
    }
    
    func setupLabels() {
        brandLabel1 = createLabel(text: "SYS.REKO.V1", size: 10, color: NSColor.white.withAlphaComponent(0.6), x: 30, y: frame.height - 45, width: 100)
        brandLabel2 = createLabel(text: "USR: XPLICTLY", size: 10, color: NSColor.white.withAlphaComponent(0.6), x: frame.width - 130, y: frame.height - 45, width: 100, alignment: .right)
        
        cpuLabel = createLabel(text: "CPU: 00.0%", size: 18, color: themeColor, x: 40, y: 35, width: 150)
        cpuLabel.shadow = createGlow(color: themeColor)
        
        memLabel = createLabel(text: "MEM: 00.0%", size: 18, color: themeColor, x: frame.width - 150 - 40, y: 35, width: 150, alignment: .right)
        memLabel.shadow = createGlow(color: themeColor)
        
        targetLockLabel = createLabel(text: "[ ACQUIRING TARGET ]", size: 11, color: themeColor, x: 0, y: frame.height / 2 + 35, width: frame.width, alignment: .center)
    }
    
    func createGlow(color: NSColor) -> NSShadow {
        let shadow = NSShadow()
        shadow.shadowColor = color
        shadow.shadowBlurRadius = 8
        shadow.shadowOffset = .zero
        return shadow
    }
    
    func updateStats() {
        cpuLabel.stringValue = String(format: "CPU: %04.1f%%", cpu)
        memLabel.stringValue = String(format: "MEM: %04.1f%%", mem)
        
        // Color shift on load
        if cpu > 80 {
            themeColor = NSColor(calibratedRed: 1.0, green: 0.1, blue: 0.2, alpha: 1.0)
            targetLockLabel.stringValue = "[ CRITICAL: HIGH LOAD ]"
        } else if cpu > 50 {
            themeColor = NSColor(calibratedRed: 1.0, green: 0.7, blue: 0.0, alpha: 1.0)
            targetLockLabel.stringValue = "[ SCANNING ANOMALIES ]"
        } else {
            themeColor = NSColor(calibratedRed: 0.0, green: 1.0, blue: 0.8, alpha: 1.0)
            targetLockLabel.stringValue = "[ TARGET LOCKED ]"
        }
        
        let glow = createGlow(color: themeColor)
        cpuLabel.textColor = themeColor
        cpuLabel.shadow = glow
        memLabel.textColor = themeColor
        memLabel.shadow = glow
        targetLockLabel.textColor = themeColor
        targetLockLabel.shadow = glow
        
        bracketsLayer.strokeColor = themeColor.cgColor
        bracketsLayer.shadowColor = themeColor.cgColor
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem?
    var window: NSWindow?
    
    var hudView: ViewfinderHUDView!

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Status bar item
        self.statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let button = statusItem?.button {
            button.title = "WW"
        }

        let menu = NSMenu()
        menu.addItem(NSMenuItem(title: "Show Desktop Widget", action: #selector(showWidget), keyEquivalent: "s"))
        menu.addItem(NSMenuItem.separator())
        menu.addItem(NSMenuItem(title: "Quit", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q"))
        statusItem?.menu = menu

        // Create a simple widget window
        let rect = NSRect(x: 200, y: 200, width: 420, height: 260)
        window = NSWindow(contentRect: rect,
                          styleMask: [.borderless, .resizable],
                          backing: .buffered,
                          defer: false)
        window?.title = "Target Lock HUD"
        window?.isMovableByWindowBackground = true
        window?.backgroundColor = .clear

        // True macOS Desktop Level Pinning
        window?.level = NSWindow.Level(rawValue: Int(CGWindowLevelKey.desktopIconWindow.rawValue))
        window?.collectionBehavior = [.canJoinAllSpaces, .stationary, .ignoresCycle]

        // Native Glassmorphism Backing
        let visualEffect = NSVisualEffectView(frame: rect)
        visualEffect.blendingMode = .behindWindow
        visualEffect.material = .hudWindow
        visualEffect.state = .active
        
        visualEffect.wantsLayer = true
        visualEffect.layer?.cornerRadius = 16
        visualEffect.layer?.masksToBounds = true
        
        window?.contentView = visualEffect

        hudView = ViewfinderHUDView(frame: rect)
        visualEffect.addSubview(hudView)

        window?.orderOut(nil)
        
        // Start IPC standard input reader
        DispatchQueue.global(qos: .background).async {
            self.readStandardInput()
        }
    }

    func readStandardInput() {
        while let line = readLine() {
            guard let data = line.data(using: .utf8) else { continue }
            do {
                if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any] {
                    DispatchQueue.main.async {
                        self.handleIPCMessage(json)
                    }
                }
            } catch {
                // Ignore parsing errors
            }
        }
    }

    func handleIPCMessage(_ json: [String: Any]) {
        guard let action = json["action"] as? String else { return }
        
        switch action {
        case "show":
            self.window?.makeKeyAndOrderFront(nil)
        case "hide":
            self.window?.orderOut(nil)
        case "update_stats":
            if let cpu = json["cpu"] as? Double {
                self.hudView.cpu = cpu
            }
            if let mem = json["mem"] as? Double {
                self.hudView.mem = mem
            }
        case "set_opacity":
            if let opacity = json["value"] as? Double {
                self.window?.alphaValue = CGFloat(opacity)
            }
        default:
            break
        }
    }

    @objc func showWidget() {
        guard let w = window else { return }
        w.makeKeyAndOrderFront(nil)
    }
}

let delegate = AppDelegate()
NSApplication.shared.delegate = delegate
NSApplication.shared.setActivationPolicy(.regular)
NSApplication.shared.run()
