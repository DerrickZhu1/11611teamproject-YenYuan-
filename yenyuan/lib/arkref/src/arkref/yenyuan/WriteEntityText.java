package arkref.yenyuan;

import java.io.PrintWriter;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import arkref.data.Document;
import arkref.data.EntityGraph;
import arkref.data.Mention;
import arkref.data.Sentence;
import edu.stanford.nlp.trees.Tree;

/**
 * Clean up the article with pronouns replaced by the first reference to the
 * referee
 * 
 * @author zhongzhu
 *
 */
public class WriteEntityText {

	private static Set<String> pronouns = new HashSet<>();
	// "I","me","my","mine","myself",
	// "you","you","your","yours","yourself",
	// "you","you","your","yours","you",
	// "he","him","his","his","himself",
	// "she","her","her","hers","herself",
	// "it","it","its","its","itself",
	// "we","us","our","ours","ourselves",
	// "you","you","your","yours","yourselves",
	// "they","them","their","theirs","themselves"
	// };

	static {
		String[] ss = new String[] { "i", "you", "he", "she", "they" };
		for (String s : ss)
			pronouns.add(s);
	}

	public static void writeReplacement(Document d, PrintWriter pw) {
		EntityGraph eg = d.entGraph();

		// pw.printf("<doc>\n");
		HashMap<String, String> entityMap = new HashMap<>();

		Set<String> replaced = new HashSet<>();
		for (Sentence s : d.sentences()) {
			// pw.printf("<sentence>\n");
			int wordnum = 0;
			for (Tree leaf : s.rootNode().getLeaves()) {

				if (wordnum > 0) {
					pw.print(" ");
				}

				boolean isMention = false;
				for (Mention m : d.mentions()) {
					List<Tree> mentionLeaves = m.node().getLeaves();
					if (mentionLeaves.get(0) == leaf) {
						String entityID = eg.entName(m);

						// remember the first mention
						if (!entityMap.containsKey(entityID)) {
							entityMap.put(entityID, leaf.yield().toString());
						}

						// only handle pronouns
						if (pronouns.contains(leaf.yield().toString().toLowerCase())) {
							// replace with the first mention
							pw.print(entityMap.get(entityID));
							isMention = true;
						}
					}
				}

				if (!isMention) {
					pw.print(leaf.yield().toString());
				}

				wordnum++;
			}

			pw.print("\n");
		}

		// pw.printf("</doc>\n");

		pw.close();
	}

}
