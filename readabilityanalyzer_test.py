import json
from readabilityanalyzer import ReadabilityAnalyzer
from properties import javaExePath, rsmJarPath, tempDirPath

if __name__ == '__main__':
    ra = ReadabilityAnalyzer(javaExePath, rsmJarPath, tempDirPath)

    print("Analyzing a method")
    results = ra.analyze_method(r"""    void turnOn() {
        isOn = true;
        System.out.println("The light is on");
    }""")
    print(json.dumps(results, indent=3))

    print("\nAnalyzing a class")
    results = ra.analyze_class(r"""class Lamp {
    boolean isOn;

    void turnOn() {
        isOn = true;
        System.out.println("The light is on");
    }

    void turnOff() {
        isOn = false;
        System.out.println("The light is off");
    }
}
""")
    print(json.dumps(results, indent=3))

    print("\nAnalyzing a file")
    results = ra.analyze_file("MyClass.java")
    print(json.dumps(results, indent=3))

    ra.cleanup()
