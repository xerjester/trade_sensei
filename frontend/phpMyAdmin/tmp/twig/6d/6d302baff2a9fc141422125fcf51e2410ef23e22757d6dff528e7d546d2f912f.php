<?php

use Twig\Environment;
use Twig\Error\LoaderError;
use Twig\Error\RuntimeError;
use Twig\Extension\SandboxExtension;
use Twig\Markup;
use Twig\Sandbox\SecurityError;
use Twig\Sandbox\SecurityNotAllowedTagError;
use Twig\Sandbox\SecurityNotAllowedFilterError;
use Twig\Sandbox\SecurityNotAllowedFunctionError;
use Twig\Source;
use Twig\Template;

/* database/data_dictionary/index.twig */
class __TwigTemplate_74d307f3a92557f57fae0c61a13d4e5b30d8f8b1c34a0bb126cab85dbb870c40 extends \Twig\Template
{
    private $source;
    private $macros = [];

    public function __construct(Environment $env)
    {
        parent::__construct($env);

        $this->source = $this->getSourceContext();

        $this->parent = false;

        $this->blocks = [
        ];
    }

    protected function doDisplay(array $context, array $blocks = [])
    {
        $macros = $this->macros;
        // line 1
        echo "<h1>";
        echo twig_escape_filter($this->env, ($context["database"] ?? null), "html", null, true);
        echo "</h1>
";
        // line 2
        if ( !twig_test_empty(($context["comment"] ?? null))) {
            // line 3
            echo "  <p>";
            echo _gettext("Database comment:");
            echo " <em>";
            echo twig_escape_filter($this->env, ($context["comment"] ?? null), "html", null, true);
            echo "</em></p>
";
        }
        // line 5
        echo "
<div>
  ";
        // line 7
        $context['_parent'] = $context;
        $context['_seq'] = twig_ensure_traversable(($context["tables"] ?? null));
        foreach ($context['_seq'] as $context["_key"] => $context["table"]) {
            // line 8
            echo "    <div>
      <h2>";
            // line 9
            echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["table"], "name", [], "any", false, false, false, 9), "html", null, true);
            echo "</h2>
      ";
            // line 10
            if ( !twig_test_empty(twig_get_attribute($this->env, $this->source, $context["table"], "comment", [], "any", false, false, false, 10))) {
                // line 11
                echo "        <p>";
                echo _gettext("Table comments:");
                echo " <em>";
                echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["table"], "comment", [], "any", false, false, false, 11), "html", null, true);
                echo "</em></p>
      ";
            }
            // line 13
            echo "
      <table class=\"pma-table print\">
        <tr>
          <th>";
            // line 16
            echo _gettext("Column");
            echo "</th>
          <th>";
            // line 17
            echo _gettext("Type");
            echo "</th>
          <th>";
            // line 18
            echo _gettext("Null");
            echo "</th>
          <th>";
            // line 19
            echo _gettext("Default");
            echo "</th>
          ";
            // line 20
            if (twig_get_attribute($this->env, $this->source, $context["table"], "has_relation", [], "any", false, false, false, 20)) {
                // line 21
                echo "            <th>";
                echo _gettext("Links to");
                echo "</th>
          ";
            }
            // line 23
            echo "          <th>";
            echo _gettext("Comments");
            echo "</th>
          ";
            // line 24
            if (twig_get_attribute($this->env, $this->source, $context["table"], "has_mime", [], "any", false, false, false, 24)) {
                // line 25
                echo "            <th>";
                echo _gettext("Media type");
                echo "</th>
          ";
            }
            // line 27
            echo "        </tr>
        ";
            // line 28
            $context['_parent'] = $context;
            $context['_seq'] = twig_ensure_traversable(twig_get_attribute($this->env, $this->source, $context["table"], "columns", [], "any", false, false, false, 28));
            foreach ($context['_seq'] as $context["_key"] => $context["column"]) {
                // line 29
                echo "          <tr>
            <td class=\"nowrap\">
              ";
                // line 31
                echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "name", [], "any", false, false, false, 31), "html", null, true);
                echo "
              ";
                // line 32
                if (twig_get_attribute($this->env, $this->source, $context["column"], "has_primary_key", [], "any", false, false, false, 32)) {
                    // line 33
                    echo "                <em>(";
                    echo _gettext("Primary");
                    echo ")</em>
              ";
                }
                // line 35
                echo "            </td>
            <td lang=\"en\" dir=\"ltr\"";
                // line 36
                echo (((("set" != twig_get_attribute($this->env, $this->source, $context["column"], "type", [], "any", false, false, false, 36)) && ("enum" != twig_get_attribute($this->env, $this->source, $context["column"], "type", [], "any", false, false, false, 36)))) ? (" class=\"nowrap\"") : (""));
                echo ">
              ";
                // line 37
                echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "print_type", [], "any", false, false, false, 37), "html", null, true);
                echo "
            </td>
            <td>";
                // line 39
                echo twig_escape_filter($this->env, ((twig_get_attribute($this->env, $this->source, $context["column"], "is_nullable", [], "any", false, false, false, 39)) ? (_gettext("Yes")) : (_gettext("No"))), "html", null, true);
                echo "</td>
            <td class=\"nowrap\">
              ";
                // line 41
                if (((null === twig_get_attribute($this->env, $this->source, $context["column"], "default", [], "any", false, false, false, 41)) && twig_get_attribute($this->env, $this->source, $context["column"], "is_nullable", [], "any", false, false, false, 41))) {
                    // line 42
                    echo "                <em>NULL</em>
              ";
                } else {
                    // line 44
                    echo "                ";
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "default", [], "any", false, false, false, 44), "html", null, true);
                    echo "
              ";
                }
                // line 46
                echo "            </td>
            ";
                // line 47
                if (twig_get_attribute($this->env, $this->source, $context["table"], "has_relation", [], "any", false, false, false, 47)) {
                    // line 48
                    echo "              <td>";
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "relation", [], "any", false, false, false, 48), "html", null, true);
                    echo "</td>
            ";
                }
                // line 50
                echo "            <td>";
                echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "comment", [], "any", false, false, false, 50), "html", null, true);
                echo "</td>
            ";
                // line 51
                if (twig_get_attribute($this->env, $this->source, $context["table"], "has_mime", [], "any", false, false, false, 51)) {
                    // line 52
                    echo "              <td>";
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "mime", [], "any", false, false, false, 52), "html", null, true);
                    echo "</td>
            ";
                }
                // line 54
                echo "          </tr>
        ";
            }
            $_parent = $context['_parent'];
            unset($context['_seq'], $context['_iterated'], $context['_key'], $context['column'], $context['_parent'], $context['loop']);
            $context = array_intersect_key($context, $_parent) + $_parent;
            // line 56
            echo "      </table>

      ";
            // line 58
            if ( !twig_test_empty(twig_get_attribute($this->env, $this->source, $context["table"], "indexes", [], "any", false, false, false, 58))) {
                // line 59
                echo "        <h3>";
                echo _gettext("Indexes");
                echo "</h3>

        <div class=\"responsivetable jsresponsive\">
          <table class=\"pma-table\" id=\"table_index\">
            <thead>
              <tr>
                <th>";
                // line 65
                echo _gettext("Keyname");
                echo "</th>
                <th>";
                // line 66
                echo _gettext("Type");
                echo "</th>
                <th>";
                // line 67
                echo _gettext("Unique");
                echo "</th>
                <th>";
                // line 68
                echo _gettext("Packed");
                echo "</th>
                <th>";
                // line 69
                echo _gettext("Column");
                echo "</th>
                <th>";
                // line 70
                echo _gettext("Cardinality");
                echo "</th>
                <th>";
                // line 71
                echo _gettext("Collation");
                echo "</th>
                <th>";
                // line 72
                echo _gettext("Null");
                echo "</th>
                <th>";
                // line 73
                echo _gettext("Comment");
                echo "</th>
              </tr>
            </thead>

            <tbody>
              ";
                // line 78
                $context['_parent'] = $context;
                $context['_seq'] = twig_ensure_traversable(twig_get_attribute($this->env, $this->source, $context["table"], "indexes", [], "any", false, false, false, 78));
                foreach ($context['_seq'] as $context["_key"] => $context["index"]) {
                    // line 79
                    echo "                ";
                    $context["columns_count"] = twig_get_attribute($this->env, $this->source, $context["index"], "getColumnCount", [], "method", false, false, false, 79);
                    // line 80
                    echo "                <tr>
                  <td rowspan=\"";
                    // line 81
                    echo twig_escape_filter($this->env, ($context["columns_count"] ?? null), "html", null, true);
                    echo "\">";
                    echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["index"], "getName", [], "method", false, false, false, 81), "html", null, true);
                    echo "</td>
                  <td rowspan=\"";
                    // line 82
                    echo twig_escape_filter($this->env, ($context["columns_count"] ?? null), "html", null, true);
                    echo "\">";
                    echo twig_escape_filter($this->env, ((twig_get_attribute($this->env, $this->source, $context["index"], "getType", [], "method", true, true, false, 82)) ? (_twig_default_filter(twig_get_attribute($this->env, $this->source, $context["index"], "getType", [], "method", false, false, false, 82), twig_get_attribute($this->env, $this->source, $context["index"], "getChoice", [], "method", false, false, false, 82))) : (twig_get_attribute($this->env, $this->source, $context["index"], "getChoice", [], "method", false, false, false, 82))), "html", null, true);
                    echo "</td>
                  <td rowspan=\"";
                    // line 83
                    echo twig_escape_filter($this->env, ($context["columns_count"] ?? null), "html", null, true);
                    echo "\">";
                    echo twig_escape_filter($this->env, ((twig_get_attribute($this->env, $this->source, $context["index"], "isUnique", [], "method", false, false, false, 83)) ? (_gettext("Yes")) : (_gettext("No"))), "html", null, true);
                    echo "</td>
                  <td rowspan=\"";
                    // line 84
                    echo twig_escape_filter($this->env, ($context["columns_count"] ?? null), "html", null, true);
                    echo "\">";
                    echo twig_get_attribute($this->env, $this->source, $context["index"], "isPacked", [], "method", false, false, false, 84);
                    echo "</td>

                  ";
                    // line 86
                    $context['_parent'] = $context;
                    $context['_seq'] = twig_ensure_traversable(twig_get_attribute($this->env, $this->source, $context["index"], "getColumns", [], "method", false, false, false, 86));
                    foreach ($context['_seq'] as $context["_key"] => $context["column"]) {
                        // line 87
                        echo "                    ";
                        if ((twig_get_attribute($this->env, $this->source, $context["column"], "getSeqInIndex", [], "method", false, false, false, 87) > 1)) {
                            // line 88
                            echo "                      <tr>
                    ";
                        }
                        // line 90
                        echo "                    <td>
                      ";
                        // line 91
                        echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "getName", [], "method", false, false, false, 91), "html", null, true);
                        echo "
                      ";
                        // line 92
                        if ( !twig_test_empty(twig_get_attribute($this->env, $this->source, $context["column"], "getSubPart", [], "method", false, false, false, 92))) {
                            // line 93
                            echo "                        (";
                            echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "getSubPart", [], "method", false, false, false, 93), "html", null, true);
                            echo ")
                      ";
                        }
                        // line 95
                        echo "                    </td>
                    <td>";
                        // line 96
                        echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "getCardinality", [], "method", false, false, false, 96), "html", null, true);
                        echo "</td>
                    <td>";
                        // line 97
                        echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "getCollation", [], "method", false, false, false, 97), "html", null, true);
                        echo "</td>
                    <td>";
                        // line 98
                        echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["column"], "getNull", [0 => true], "method", false, false, false, 98), "html", null, true);
                        echo "</td>

                    ";
                        // line 100
                        if ((twig_get_attribute($this->env, $this->source, $context["column"], "getSeqInIndex", [], "method", false, false, false, 100) == 1)) {
                            // line 101
                            echo "                      <td rowspan=\"";
                            echo twig_escape_filter($this->env, ($context["columns_count"] ?? null), "html", null, true);
                            echo "\">";
                            echo twig_escape_filter($this->env, twig_get_attribute($this->env, $this->source, $context["index"], "getComments", [], "method", false, false, false, 101), "html", null, true);
                            echo "</td>
                    ";
                        }
                        // line 103
                        echo "                </tr>
                  ";
                    }
                    $_parent = $context['_parent'];
                    unset($context['_seq'], $context['_iterated'], $context['_key'], $context['column'], $context['_parent'], $context['loop']);
                    $context = array_intersect_key($context, $_parent) + $_parent;
                    // line 105
                    echo "              ";
                }
                $_parent = $context['_parent'];
                unset($context['_seq'], $context['_iterated'], $context['_key'], $context['index'], $context['_parent'], $context['loop']);
                $context = array_intersect_key($context, $_parent) + $_parent;
                // line 106
                echo "            </tbody>
          </table>
        </div>
      ";
            } else {
                // line 110
                echo "        <p>";
                echo _gettext("No index defined!");
                echo "</p>
      ";
            }
            // line 112
            echo "    </div>
  ";
        }
        $_parent = $context['_parent'];
        unset($context['_seq'], $context['_iterated'], $context['_key'], $context['table'], $context['_parent'], $context['loop']);
        $context = array_intersect_key($context, $_parent) + $_parent;
        // line 114
        echo "</div>

<p class=\"print_ignore\">
  <input type=\"button\" class=\"btn btn-secondary button\" id=\"print\" value=\"";
        // line 117
        echo _gettext("Print");
        echo "\">
</p>
";
    }

    public function getTemplateName()
    {
        return "database/data_dictionary/index.twig";
    }

    public function isTraitable()
    {
        return false;
    }

    public function getDebugInfo()
    {
        return array (  382 => 117,  377 => 114,  370 => 112,  364 => 110,  358 => 106,  352 => 105,  345 => 103,  337 => 101,  335 => 100,  330 => 98,  326 => 97,  322 => 96,  319 => 95,  313 => 93,  311 => 92,  307 => 91,  304 => 90,  300 => 88,  297 => 87,  293 => 86,  286 => 84,  280 => 83,  274 => 82,  268 => 81,  265 => 80,  262 => 79,  258 => 78,  250 => 73,  246 => 72,  242 => 71,  238 => 70,  234 => 69,  230 => 68,  226 => 67,  222 => 66,  218 => 65,  208 => 59,  206 => 58,  202 => 56,  195 => 54,  189 => 52,  187 => 51,  182 => 50,  176 => 48,  174 => 47,  171 => 46,  165 => 44,  161 => 42,  159 => 41,  154 => 39,  149 => 37,  145 => 36,  142 => 35,  136 => 33,  134 => 32,  130 => 31,  126 => 29,  122 => 28,  119 => 27,  113 => 25,  111 => 24,  106 => 23,  100 => 21,  98 => 20,  94 => 19,  90 => 18,  86 => 17,  82 => 16,  77 => 13,  69 => 11,  67 => 10,  63 => 9,  60 => 8,  56 => 7,  52 => 5,  44 => 3,  42 => 2,  37 => 1,);
    }

    public function getSourceContext()
    {
        return new Source("", "database/data_dictionary/index.twig", "E:\\STUDENT\\phpMyAdmin\\templates\\database\\data_dictionary\\index.twig");
    }
}
