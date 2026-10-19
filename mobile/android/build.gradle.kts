allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

val newBuildDir: Directory =
    rootProject.layout.buildDirectory
        .dir("../../build")
        .get()
rootProject.layout.buildDirectory.value(newBuildDir)

subprojects {
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
}
subprojects {
    project.evaluationDependsOn(":app")
    afterEvaluate {
        if (project.hasProperty("android")) {
            val androidExt = project.extensions.findByName("android")
            if (androidExt != null) {
                try {
                    val getNs = androidExt.javaClass.getMethod("getNamespace")
                    val currentNs = getNs.invoke(androidExt)
                    if (currentNs == null) {
                        val setNs = androidExt.javaClass.getMethod("setNamespace", String::class.java)
                        val pkg = if (project.group.toString().isNotEmpty()) project.group.toString() else "com.safetychecker.${project.name.replace("-", "_")}"
                        setNs.invoke(androidExt, pkg)
                    }
                } catch (_: Exception) {}
            }
        }
    }
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
