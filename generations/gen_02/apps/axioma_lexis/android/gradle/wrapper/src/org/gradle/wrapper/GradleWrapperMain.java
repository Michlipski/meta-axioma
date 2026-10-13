package org.gradle.wrapper;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.zip.*;

public class GradleWrapperMain {
    public static void main(String[] args) {
        try {
            // Locate project directory relative to this JAR's location (gradle/wrapper/gradle-wrapper.jar -> android/)
            File jarFile = new File(GradleWrapperMain.class.getProtectionDomain().getCodeSource().getLocation().toURI());
            File wrapperDir = jarFile.getParentFile();
            File projectDir = wrapperDir.getParentFile().getParentFile();
            File propsFile = new File(wrapperDir, "gradle-wrapper.properties");
            
            String distUrl = "https://services.gradle.org/distributions/gradle-8.4-bin.zip";
            if (propsFile.exists()) {
                Properties props = new Properties();
                try (InputStream in = new FileInputStream(propsFile)) {
                    props.load(in);
                }
                String configured = props.getProperty("distributionUrl");
                if (configured != null && !configured.trim().isEmpty()) {
                    distUrl = configured.trim().replace("\\:", ":");
                }
            }

            // Gradle home directory in ~/.gradle
            String userHome = System.getProperty("user.home");
            File gradleDists = new File(userHome, ".gradle/wrapper/dists/gradle-8.4-bin");
            File gradleDir = null;

            if (gradleDists.exists()) {
                File[] subs = gradleDists.listFiles();
                if (subs != null) {
                    for (File sub : subs) {
                        File candidate = new File(sub, "gradle-8.4/bin/gradle");
                        if (candidate.exists()) {
                            gradleDir = new File(sub, "gradle-8.4");
                            break;
                        }
                    }
                }
            }

            File localExtract = new File(wrapperDir, "gradle-8.4");
            if (localExtract.exists() && new File(localExtract, "bin/gradle").exists()) {
                gradleDir = localExtract;
            }

            if (gradleDir == null) {
                System.out.println("[gradle-wrapper] Downloading Gradle from " + distUrl + "...");
                File zipFile = new File(wrapperDir, "gradle-8.4-bin.zip");
                wrapperDir.mkdirs();

                downloadFile(distUrl, zipFile);
                System.out.println("[gradle-wrapper] Extracting to " + localExtract.getAbsolutePath() + "...");
                unzip(zipFile, wrapperDir);
                zipFile.delete();
                gradleDir = localExtract;
            }

            File gradleBin = new File(gradleDir, "bin/gradle");
            gradleBin.setExecutable(true);

            List<String> cmd = new ArrayList<>();
            cmd.add(gradleBin.getAbsolutePath());
            for (String arg : args) {
                cmd.add(arg);
            }

            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.directory(projectDir);
            pb.inheritIO();
            
            String javaHome = System.getenv("JAVA_HOME");
            if (javaHome == null || javaHome.isEmpty()) {
                File studioJava = new File("/Applications/Android Studio.app/Contents/jbr/Contents/Home");
                if (studioJava.exists()) {
                    pb.environment().put("JAVA_HOME", studioJava.getAbsolutePath());
                }
            }

            Process process = pb.start();
            int exitCode = process.waitFor();
            System.exit(exitCode);
        } catch (Exception e) {
            System.err.println("[gradle-wrapper] Error: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }

    private static void downloadFile(String urlStr, File target) throws IOException {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setInstanceFollowRedirects(true);
        conn.setConnectTimeout(15000);
        conn.setReadTimeout(30000);

        int status = conn.getResponseCode();
        if (status == HttpURLConnection.HTTP_MOVED_TEMP || status == HttpURLConnection.HTTP_MOVED_PERM || status == 307 || status == 308) {
            String newUrl = conn.getHeaderField("Location");
            downloadFile(newUrl, target);
            return;
        }

        try (InputStream in = conn.getInputStream();
             OutputStream out = new FileOutputStream(target)) {
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) {
                out.write(buf, 0, n);
            }
        }
    }

    private static void unzip(File zipFile, File destDir) throws IOException {
        try (ZipInputStream zipIn = new ZipInputStream(new FileInputStream(zipFile))) {
            ZipEntry entry;
            while ((entry = zipIn.getNextEntry()) != null) {
                File file = new File(destDir, entry.getName());
                if (entry.isDirectory()) {
                    file.mkdirs();
                } else {
                    file.getParentFile().mkdirs();
                    try (OutputStream out = new FileOutputStream(file)) {
                        byte[] buf = new byte[8192];
                        int n;
                        while ((n = zipIn.read(buf)) > 0) {
                            out.write(buf, 0, n);
                        }
                    }
                }
                zipIn.closeEntry();
            }
        }
    }
}
