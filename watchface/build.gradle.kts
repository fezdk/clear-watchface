plugins { id("com.android.application") }

android {
    namespace = "dk.nezar.clearwatchface"
    compileSdk = 36
    // Remove AGP's generated R classes from this resource-only WFF package.
    buildTypes.all {
        isMinifyEnabled = true
        isShrinkResources = false
        proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
    }
    defaultConfig {
        applicationId = "dk.nezar.clearwatchface"
        minSdk = 35
        targetSdk = 36
        versionCode = 3
        versionName = "0.2.1"
    }
}

val validateWatchface by tasks.registering(JavaExec::class) {
    group = "verification"
    description = "Validate the WFF 2 XML with Google's official schema validator."
    classpath = files(rootProject.file("tools/wff-validator.jar"))
    mainClass.set("com.samsung.watchface.DWFValidationApplication")
    args("2", file("src/main/res/raw/watchface.xml").absolutePath)
}
tasks.named("preBuild") { dependsOn(validateWatchface) }
