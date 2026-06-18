# ... (Keep all your existing imports and setup from the previous code) ...

# --- REPLACE THE 'Execute Core Strategy Brief' BLOCK (PANE 3) ---
            if st.button("Execute Core Strategy Brief", use_container_width=True):
                with st.spinner("Synthesizing formal Briefing Memorandum..."):
                    try:
                        client = genai.Client(api_key=st.session_state.stored_api_key)
                        # We force the AI to adopt a formal legal memorandum structure
                        prompt = """
                        Generate a formal 'Case Briefing Memorandum' in the following format:
                        # Case Briefing Memorandum
                        ## 1. Executive Summary
                        [Concise overview of the dispute]
                        ## 2. Core Legal Issues
                        [Bulleted list of issues]
                        ## 3. Evidence Chronology Highlights
                        [Key events linked to page citations]
                        ## 4. Precedents & Strategic Risks
                        [Legal risks and recommended stance]
                        ## 5. Recommended Hearing Preparation Notes
                        [Actionable points for the counsel]
                        
                        Cite all claims with [Page X, Para Y]. Keep tone authoritative.
                        """
                        contents = [prompt] + st.session_state.gemini_files
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=contents,
                            config=types.GenerateContentConfig(system_instruction=PESHI_SYSTEM_INSTRUCTION)
                        )
                        st.session_state.last_analysis = response.text
                    except Exception as e:
                        st.error(f"Analysis fault: {e}")

            if st.session_state.last_analysis:
                st.divider()
                st.markdown(st.session_state.last_analysis)
                
                # New Export button that specifically titles the download for professional use
                st.download_button(
                    label="📥 Download Briefing Memo (.txt)",
                    data=st.session_state.last_analysis,
                    file_name="Briefing_Memorandum.txt",
                    mime="text/plain",
                    use_container_width=True
                )
# ... (Keep the rest of the file as is) ...