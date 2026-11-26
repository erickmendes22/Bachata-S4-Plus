package com.bachatas4.android.patches;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

/** Keep existing choices when the installer creates a new, verified runtime tree.
 *
 * Only isEnabled values migrate. Instructions, conditions, names and all other
 * bytes remain those of the new bundled catalogue. This helper does not install
 * a runtime or apply a game patch; it runs before the existing selector/launcher.
 */
public final class OrderPatchCatalog {
    private static final String VERSION = "order1886-0102-port-v1";
    private static final String RELATIVE = "patches/bachata-official/TheOrder1886.xml";
    private static final String MARKER = ".order1886-port-selection-v1";
    private static final String[] IDENTITY = {"Title", "Name", "Author", "AppVer", "AppElf"};
    private static final int MAX_XML_BYTES = 2 * 1024 * 1024;
    private static final Pattern ENABLED = Pattern.compile("(\\bisEnabled\\s*=\\s*)([\"'])([^\"']*)([\"'])");

    private OrderPatchCatalog() {}

    public static void prepare(Path runtimeRoot) {
        if (runtimeRoot != null) prepare(runtimeRoot.toFile());
    }

    public static synchronized void prepare(File runtimeRoot) {
        if (runtimeRoot == null) return;
        try {
            File root = runtimeRoot.getCanonicalFile();
            File current = new File(root, "user/" + RELATIVE);
            File baseline = new File(root, RELATIVE);
            if (!current.isFile() || !baseline.isFile()) return;
            File marker = new File(current.getParentFile(), MARKER);
            if (marker.isFile()) return;
            // Selector and native service are distinct Android processes.
            try (RandomAccessFile lockFile = new RandomAccessFile(
                     new File(current.getParentFile(), MARKER + ".lock"), "rw");
                 FileChannel channel = lockFile.getChannel(); FileLock lock = channel.lock()) {
                if (!lock.isValid()) throw new IOException("Catalogue lock unavailable");
                if (marker.isFile()) return;
                byte[] original = read(current);
                byte[] bundled = read(baseline);
                Catalog target = parse(original);
                Catalog immutable = parse(bundled);
                if (!VERSION.equals(target.version) || !VERSION.equals(immutable.version)) return;
                if (!Arrays.equals(original, bundled)) {
                    // A choice was already saved in this runtime. Never overwrite it
                    // with an older runtime, including an explicit all-disabled save.
                    atomicWrite(marker, "current runtime already edited\n".getBytes(StandardCharsets.UTF_8));
                    return;
                }
                Source previous = newestEditedSource(root);
                if (previous == null) return;
                byte[] updated = merge(original, target, previous.catalog);
                // Recheck after reading older runtimes. An external selector may
                // have saved while this helper was scanning; its edit has priority.
                if (!Arrays.equals(original, read(current))) return;
                if (!Arrays.equals(original, updated)) atomicWrite(current, updated);
                atomicWrite(marker, ("migrated selection " + previous.modified + "\n")
                                      .getBytes(StandardCharsets.UTF_8));
                System.err.println("BACHATA_ORDER102_CATALOG_SELECTION_MIGRATED");
            }
        } catch (Exception failure) {
            // Missing or malformed history must not replace a valid catalogue,
            // prevent the selector opening, or prevent the game launching.
            System.err.println("BACHATA_ORDER102_CATALOG_SELECTION_SKIPPED "
                               + failure.getClass().getSimpleName());
        }
    }

    private static byte[] read(File file) throws IOException {
        if (file.length() <= 0 || file.length() > MAX_XML_BYTES)
            throw new IOException("Invalid catalogue size");
        byte[] bytes = Files.readAllBytes(file.toPath());
        if (bytes.length <= 0 || bytes.length > MAX_XML_BYTES)
            throw new IOException("Catalogue size changed");
        return bytes;
    }

    private static String utf8(byte[] bytes) throws IOException {
        return StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(bytes)).toString();
    }

    private static Catalog parse(byte[] bytes) throws Exception {
        String text = utf8(bytes);
        if (text.contains("<!DOCTYPE")) throw new IOException("DTD is not a patch catalogue");
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(false);
        factory.setExpandEntityReferences(false);
        DocumentBuilder builder = factory.newDocumentBuilder();
        builder.setEntityResolver((publicId, systemId) -> {
            throw new SAXException("External entities are not patch definitions");
        });
        Document doc = builder.parse(new ByteArrayInputStream(bytes));
        Element root = doc.getDocumentElement();
        if (!"Patch".equals(root.getTagName())) throw new IOException("Not a patch catalogue");
        boolean order = false;
        NodeList ids = root.getElementsByTagName("ID");
        for (int i = 0; i < ids.getLength(); ++i)
            order |= "CUSA00785".equals(ids.item(i).getTextContent());
        if (!order) throw new IOException("Not an Order catalogue");
        Catalog result = new Catalog(root.getAttribute("BachataPortCatalog"));
        NodeList nodes = root.getChildNodes();
        for (int i = 0; i < nodes.getLength(); ++i) {
            Node node = nodes.item(i);
            if (!(node instanceof Element) || !"Metadata".equals(node.getNodeName())) continue;
            Element element = (Element) node;
            StringBuilder key = new StringBuilder();
            for (String field : IDENTITY) {
                String value = element.getAttribute(field);
                key.append(value.length()).append(':').append(value);
            }
            String enabled = element.getAttribute("isEnabled");
            if (!enabled.isEmpty() && !"true".equals(enabled) && !"false".equals(enabled))
                throw new IOException("Invalid enabled selection");
            if (result.choices.put(key.toString(), "true".equals(enabled)) != null)
                throw new IOException("Ambiguous patch identity");
        }
        if (result.choices.isEmpty()) throw new IOException("Empty patch catalogue");
        return result;
    }

    private static Source newestEditedSource(File currentRoot) throws Exception {
        File parent = currentRoot.getParentFile();
        File[] runtimes = parent == null ? null : parent.listFiles();
        if (runtimes == null) return null;
        List<File> newest = new ArrayList<>();
        long modified = Long.MIN_VALUE;
        for (File candidate : runtimes) {
            if (!candidate.isDirectory() || !candidate.getName().startsWith("bachata-s4-plus-")) continue;
            File resolved = candidate.getCanonicalFile();
            if (!parent.equals(resolved.getParentFile()) || currentRoot.equals(resolved)) continue;
            File user = new File(resolved, "user/" + RELATIVE);
            File immutable = new File(resolved, RELATIVE);
            if (!user.isFile() || !immutable.isFile()) continue;
            // Both bundled copies start identical. A difference is evidence of
            // an actual saved selection, even when every option was turned off.
            if (Arrays.equals(read(user), read(immutable))) continue;
            long timestamp = user.lastModified();
            if (timestamp > modified) {
                newest.clear();
                modified = timestamp;
            }
            if (timestamp == modified) newest.add(user);
        }
        Source selected = null;
        for (File file : newest) {
            // Do not silently resurrect older choices if the newest edited
            // catalogue is malformed or equally recent candidates disagree.
            Catalog catalog = parse(read(file));
            File sourceRoot = file.getParentFile().getParentFile().getParentFile().getParentFile();
            parse(read(new File(sourceRoot, RELATIVE)));
            if (selected != null && !selected.catalog.choices.equals(catalog.choices))
                throw new IOException("Equally recent selections disagree");
            selected = new Source(catalog, modified);
        }
        return selected;
    }

    private static byte[] merge(byte[] original, Catalog target, Catalog source) throws Exception {
        String text = utf8(original);
        List<int[]> tags = metadataTags(text);
        if (tags.size() != target.choices.size()) throw new IOException("Metadata layout mismatch");
        StringBuilder result = new StringBuilder(text.length() + 128);
        int index = 0, cursor = 0;
        for (Map.Entry<String, Boolean> entry : target.choices.entrySet()) {
            int[] tag = tags.get(index++);
            result.append(text, cursor, tag[0]);
            String opening = text.substring(tag[0], tag[1]);
            Boolean enabled = source.choices.get(entry.getKey());
            if (enabled != null && !enabled.equals(entry.getValue())) {
                int[] attribute = enabledValue(opening);
                if (attribute != null) {
                    opening = opening.substring(0, attribute[0]) + enabled.toString()
                              + opening.substring(attribute[1]);
                } else {
                    int at = opening.endsWith("/>") ? opening.length() - 2 : opening.length() - 1;
                    opening = opening.substring(0, at) + " isEnabled=\"" + enabled + "\""
                              + opening.substring(at);
                }
            }
            result.append(opening);
            cursor = tag[1];
        }
        result.append(text, cursor, text.length());
        byte[] bytes = result.toString().getBytes(StandardCharsets.UTF_8);
        Catalog verified = parse(bytes);
        for (Map.Entry<String, Boolean> entry : verified.choices.entrySet()) {
            Boolean wanted = source.choices.get(entry.getKey());
            if (wanted == null) wanted = target.choices.get(entry.getKey());
            if (!entry.getValue().equals(wanted)) throw new IOException("Selection merge mismatch");
        }
        return bytes;
    }

    private static int[] enabledValue(String opening) {
        Matcher candidate = ENABLED.matcher(opening);
        while (candidate.find()) {
            char quote = 0;
            for (int i = 0; i < candidate.start(); ++i) {
                char value = opening.charAt(i);
                if (quote != 0) { if (value == quote) quote = 0; }
                else if (value == '\'' || value == '"') quote = value;
            }
            // A note is allowed to mention text resembling an XML attribute.
            if (quote == 0) return new int[] {candidate.start(3), candidate.end(3)};
        }
        return null;
    }

    private static List<int[]> metadataTags(String text) throws IOException {
        List<int[]> result = new ArrayList<>();
        for (int at = 0; (at = text.indexOf('<', at)) >= 0;) {
            String endToken = text.startsWith("<!--", at) ? "-->"
                : text.startsWith("<![CDATA[", at) ? "]]>" : text.startsWith("<?", at) ? "?>" : null;
            if (endToken != null) {
                int end = text.indexOf(endToken, at + 2);
                if (end < 0) throw new IOException("Unterminated XML token");
                at = end + endToken.length();
                continue;
            }
            int end = at + 1;
            char quote = 0;
            for (; end < text.length(); ++end) {
                char value = text.charAt(end);
                if (quote != 0) { if (value == quote) quote = 0; }
                else if (value == '\'' || value == '"') quote = value;
                else if (value == '>') break;
            }
            if (end == text.length()) throw new IOException("Unterminated XML tag");
            int boundary = at + "<Metadata".length();
            if (text.startsWith("<Metadata", at) && boundary <= end
                && (Character.isWhitespace(text.charAt(boundary)) || text.charAt(boundary) == '>'
                    || text.charAt(boundary) == '/')) result.add(new int[] {at, end + 1});
            at = end + 1;
        }
        return result;
    }

    private static void atomicWrite(File target, byte[] bytes) throws IOException {
        Path temp = Files.createTempFile(target.getParentFile().toPath(), ".order102-", ".tmp");
        try {
            try (FileOutputStream out = new FileOutputStream(temp.toFile())) {
                out.write(bytes);
                out.getFD().sync();
            }
            Files.move(temp, target.toPath(), StandardCopyOption.ATOMIC_MOVE,
                       StandardCopyOption.REPLACE_EXISTING);
        } finally {
            Files.deleteIfExists(temp);
        }
    }

    private static final class Catalog {
        final String version;
        final LinkedHashMap<String, Boolean> choices = new LinkedHashMap<>();
        Catalog(String version) { this.version = version; }
    }

    private static final class Source {
        final Catalog catalog;
        final long modified;
        Source(Catalog catalog, long modified) { this.catalog = catalog; this.modified = modified; }
    }
}
