
import sys
import os
sys.path.append(os.getcwd())

from PyQt6.QtWidgets import QApplication
from app.widgets.base_widget import create_widget, WIDGET_REGISTRY

def test_widgets():
    app = QApplication(sys.argv)
    
    widgets_to_test = ["pomodoro", "stock", "todo", "calculator", "countdown"]
    all_passed = True
    
    print("--- Testing New Widgets ---")
    
    from PyQt6.QtCore import QPoint, QSize
    
    for w_type in widgets_to_test:
        print(f"\nTesting {w_type}...")
        
        # Check registry
        if w_type not in WIDGET_REGISTRY:
            print(f"❌ {w_type} NOT in WIDGET_REGISTRY")
            all_passed = False
            continue
        print(f"✅ {w_type} found in registry")
        
        # Create widget
        try:
            widget = create_widget(w_type, widget_id=f"test_{w_type}", position=QPoint(100, 100), size=QSize(200, 200))
            if widget:
                print(f"✅ {w_type} instantiated successfully: {widget}")
                # Check specifics
                if w_type == "pomodoro":
                    if hasattr(widget, "timer"):
                         print("   ✅ Pomodoro timer attribute found")
                elif w_type == "stock":
                    if hasattr(widget, "symbol_label"):
                         print("   ✅ Stock UI elements found")
                elif w_type == "todo":
                     if hasattr(widget, "list_widget"):
                         print("   ✅ To-Do list widget found")
                
                widget.close()
            else:
                print(f"❌ {w_type} failed to instantiate (returned None)")
                all_passed = False
        except Exception as e:
            print(f"❌ {w_type} raising exception during instantiation: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    if all_passed:
        print("\n🎉 All new widgets passed basic instantiation tests!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed.")
        sys.exit(1)

if __name__ == "__main__":
    test_widgets()
