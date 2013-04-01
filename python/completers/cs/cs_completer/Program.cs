using System;
using ICSharpcode.NRefactory.CSharp.Completion;

class Program
{
    static void Main(string[] args)
    {
        string source = "Hi";
        string filename = "Hi.cs";

        ReadOnlyDocument document = new ReadOnlyDocument(source);
        CSharpUnresolvedFile unresolvedFile = new CSharpUnresolvedFile(filename);
        DefaultCompletionContextProvider completionContextProvider = new DefaultCompletionContextProvider(document, unresolvedFile);
        ICompletionDataFactory factory = new ICompletionDataFactory();
        IProjectContent content = new IProjectContent();
        CSharpTypeResolveContext ctx = new CSharpTypeResolveContext();

        CSharpCompletionEngine completer = new CSharpCompletionEngine(document, completionContextProvider, factory, content, ctx);
    }
}
