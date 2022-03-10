import curses


class SearchUI:
    """
    Defines a set of curses terminal pages, where each page can be thought of as a state in a state machine.
    """

    GREEN = 1
    BLUE = 2
    RED = 3

    def __init__(self, screen):
        self._screen = screen
        curses.echo()
        curses.init_pair(self.GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(self.BLUE, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(self.RED, curses.COLOR_RED, curses.COLOR_BLACK)

    def query_page(self):
        """
        Run the query page and return the query entered.
        """
        self._screen.clear()
        self._screen.addstr("Welcome to Search!", curses.color_pair(self.GREEN))
        self._screen.addstr(1, 0, "Enter a query below (empty query exits)", curses.color_pair(self.GREEN))
        self._screen.addstr(3, 0, "Q:> ", curses.color_pair(self.RED))
        return self._screen.getstr().decode('utf-8')

    def query_results_page(self, results, query, page_num):
        """
        Run the query results page and return the next-state key selected.
        """
        self._screen.clear()
        self._screen.addstr(0, 0, "Results for query: ", curses.color_pair(self.GREEN))
        self._screen.addstr("{}".format(query), curses.color_pair(self.RED))
        self._screen.addstr(1, 0, "Page {}".format(page_num), curses.color_pair(self.GREEN))

        y, _ = self._screen.getyx()
        height_header = y + 2
        height_footer = 3

        # Create a pad on which to print the search results and which we can scroll up and down.
        screen_ymax, screen_xmax = self._screen.getmaxyx()
        results_pad = curses.newpad(1000, screen_xmax)
        results_pad_visible_height = screen_ymax - height_header - height_footer

        # Print the results onto the pad
        n, y = 0, 0
        for result in results:
            # Print the number, similarity score, and doc id of the result
            results_pad.addstr(y, 0, "[{}] ".format(n), curses.color_pair(self.BLUE))
            results_pad.addstr("({:0.2f}) {} ".format(result[0], result[1]), curses.color_pair(self.RED))
            y += 1

            # Print the Title of the result
            title_lines = result[2].split('\n')
            for line in title_lines:
                # If title has an empty line within it we just increment the current y position
                if not line:
                    y += 1
                # Split each line into chunks that fit the screen width
                chunk_size = screen_xmax - 1
                for chunk in [line[x:x + chunk_size] for x in range(0, len(line), chunk_size)]:
                    results_pad.addstr(y, 0, chunk)
                    y += 1

            # Increment the results printed counter n, and add a space between results by incrementing y
            n += 1
            y += 1

        # Record number of lines of results print
        nlines = y - 1

        # Print the controls message at the bottom of the screen
        self._screen.addstr(screen_ymax - 2, 0, "<0-9>", curses.color_pair(self.BLUE))
        self._screen.addstr(" select document, ", curses.color_pair(self.GREEN))
        self._screen.addstr("<u>", curses.color_pair(self.BLUE))
        self._screen.addstr("p, ", curses.color_pair(self.GREEN))
        self._screen.addstr("<d>", curses.color_pair(self.BLUE))
        self._screen.addstr("own, ", curses.color_pair(self.GREEN))
        self._screen.addstr("<p>", curses.color_pair(self.BLUE))
        self._screen.addstr("rev page, ", curses.color_pair(self.GREEN))
        self._screen.addstr("<n>", curses.color_pair(self.BLUE))
        self._screen.addstr("ext page, ", curses.color_pair(self.GREEN))
        self._screen.addstr("<q>", curses.color_pair(self.BLUE))
        self._screen.addstr("uit ", curses.color_pair(self.GREEN))
        self._screen.addstr("<b>", curses.color_pair(self.BLUE))
        self._screen.addstr("ack", curses.color_pair(self.GREEN))

        # Create the set of keys that correspond to a change in state
        state_change_keys = {'p', 'n', 'q', 'b'}
        state_change_keys.update(map(str, range(10)))

        # Display the results pad and scroll it up and down if up and down keys are used
        # Exit display/scroll if a valid state change key is issued
        line_num = 0
        while True:
            self._screen.refresh()
            results_pad.refresh(line_num, 0, height_header, 0, screen_ymax - 1 - height_footer, screen_xmax - 1)
            key = self._screen.getkey(screen_ymax - 1, 0)
            if key == 'u':
                line_num = max(0, line_num - 1)
            elif key == 'd':
                if nlines <= results_pad_visible_height:
                    continue
                line_num = min(nlines - results_pad_visible_height, line_num + 1)
            elif key in state_change_keys:
                break
            else:
                continue

        return key

    def document_page(self, document_text):
        """
        Displays the provided document text and returns the state change key selected.
        """
        self._screen.clear()

        height_header = 0
        height_footer = 3

        # Create a pad on which to print the document and which we can scroll up and down.
        screen_ymax, screen_xmax = self._screen.getmaxyx()
        doctext_pad = curses.newpad(5000, screen_xmax)
        doctext_pad_visible_height = screen_ymax - height_header - height_footer

        # Print the document onto the pad
        y = 0
        doc_lines = document_text.split('\n')
        for line in doc_lines:
            # For empty lines we just increment the line position
            if not line:
                y += 1
            # Split each line into chunks that fit the screen width
            chunk_size = screen_xmax - 1
            for chunk in [line[x:x + chunk_size] for x in range(0, len(line), chunk_size)]:
                doctext_pad.addstr(y, 0, chunk)
                y += 1

        # Record number of lines of document print
        nlines = y - 1

        # Print the controls message at the bottom of the screen
        self._screen.addstr(screen_ymax - 2, 0, "<u>", curses.color_pair(self.BLUE))
        self._screen.addstr("p, ", curses.color_pair(self.GREEN))
        self._screen.addstr("<d>", curses.color_pair(self.BLUE))
        self._screen.addstr("own, ", curses.color_pair(self.GREEN))
        self._screen.addstr("<q>", curses.color_pair(self.BLUE))
        self._screen.addstr("uit ", curses.color_pair(self.GREEN))
        self._screen.addstr("<b>", curses.color_pair(self.BLUE))
        self._screen.addstr("ack", curses.color_pair(self.GREEN))

        # Create the set of keys that correspond to a change in state
        state_change_keys = {'q', 'b'}

        # Display the results pad and scroll it up and down if up and down keys are used
        # Exit display/scroll if a valid state change key is issued
        line_num = 0
        while True:
            self._screen.refresh()
            doctext_pad.refresh(line_num, 0, height_header, 0, screen_ymax - 1 - height_footer, screen_xmax - 1)
            key = self._screen.getkey(screen_ymax - 1, 0)
            if key == 'u':
                line_num = max(0, line_num - 1)
            elif key == 'd':
                if nlines <= doctext_pad_visible_height:
                    continue
                line_num = min(nlines - doctext_pad_visible_height, line_num + 1)
            elif key in state_change_keys:
                break
            else:
                continue

        return key
